"""
Dynamic pilot module that uses the task registry instead of hardcoded tasks.

This replaces the hardcoded task constants and functions with a flexible
system that can execute any registered task type.
"""

import time
import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .controller import FleetController
from .task_registry import task_registry, TaskExecutor
from .edge_bridge import InMemoryEventSink
from .mock_twin import LocalTwinProjector
from .robot_manager import sdk_available


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Import log_utils after path setup
from data import log_utils

logger = logging.getLogger(__name__)


class DynamicTaskExecutor:
    """Dynamic task execution engine."""
    
    def __init__(self):
        self.task_registry = task_registry
        # Auto-discover tasks from modules
        self.task_registry.auto_discover_tasks()
        logger.info(f"Loaded {len(self.task_registry.list_tasks())} task types")
    
    def execute_task(
        self,
        controller: FleetController,
        robot_id: str,
        task_id: str,
        task_spec: Dict[str, Any],
        *,
        projector: Optional[LocalTwinProjector] = None,
        sink: Optional[InMemoryEventSink] = None,
    ) -> Dict[str, Any]:
        """
        Execute a task using dynamic task registry.
        
        Args:
            controller: FleetController instance
            robot_id: ID of robot to execute task
            task_id: Unique task identifier
            task_spec: Task specification with type and parameters
            projector: Optional digital twin projector
            sink: Optional event sink
            
        Returns:
            Dict with execution results
        """
        # Get robot from controller
        robot = controller.get_robot(robot_id)
        if not robot:
            return {"success": False, "error": f"Robot {robot_id} not found"}
        
        # Extract task type and parameters
        task_type = task_spec.get("type")
        if not task_type:
            return {"success": False, "error": "Task type not specified"}
        
        # Get executor from registry
        executor = self.task_registry.get_executor(task_type)
        if not executor:
            available_tasks = self.task_registry.list_tasks()
            return {
                "success": False, 
                "error": f"Unknown task type: {task_type}. Available: {available_tasks}"
            }
        
        # Validate task specification
        if not executor.validate_spec(task_spec):
            return {"success": False, "error": f"Invalid task specification for {task_type}"}
        
        # Log task start
        log_utils.log_task_start(task_id, robot_id, task_spec)
        log_utils.log_robot_status(robot_id, {"status": "busy", "task_id": task_id})
        
        # Create task status event
        started_event = controller.make_task_status_event(
            robot_id,
            task_id,
            "started",
            summary=f"Started {task_type}",
            details={"task_spec": task_spec},
        )
        
        if sink:
            sink.publish(f"fleet/tasks/{robot_id}/started", started_event)
        if projector:
            projector.ingest(started_event)
        
        # Execute the task
        start_time = time.perf_counter()
        try:
            logger.debug(f"About to execute task {task_id} with spec: {task_spec}")
            result = executor.execute(robot, task_spec)
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            result = {"success": False, "error": str(e)}
        
        duration = time.perf_counter() - start_time
        
        # Log task completion
        log_utils.log_task_end(task_id, robot_id, result, duration)
        
        # Report completion to controller
        controller.report_task_done(robot_id, task_id, result)
        log_utils.log_robot_status(robot_id, {"status": "idle", "last_task": task_id})
        
        # Create completion event
        status = "completed" if result.get("success") else "failed"
        completed_event = controller.make_task_status_event(
            robot_id,
            task_id,
            status,
            summary=f"Finished {self.task_registry.get_capability(task_type).description}",
            details={
                "task_spec": task_spec, 
                "result": result, 
                "duration_sec": round(duration, 3)
            },
        )
        
        if sink:
            sink.publish(f"fleet/tasks/{robot_id}/completed", completed_event)
        if projector:
            projector.ingest(completed_event)
        
        # Create alert if failed
        if not result.get("success"):
            alert = controller.make_alert_event(
                robot_id,
                severity="warning",
                code="task_failure",
                message=f"Task {task_id} failed",
                details={"task_id": task_id, "result": result},
            )
            if sink:
                sink.publish(f"fleet/alerts/{robot_id}", alert)
            if projector:
                projector.ingest(alert)
        
        return result
    
    def get_compatible_tasks(self, robot_id: str, controller: FleetController) -> Dict[str, Any]:
        """
        Get tasks compatible with a specific robot.
        
        Returns:
            Dict with compatible task types and their capabilities
        """
        robot = controller.get_robot(robot_id)
        if not robot:
            return {"error": f"Robot {robot_id} not found"}
        
        # Get robot capabilities
        robot_capabilities = getattr(robot, 'capabilities', [])
        robot_type = getattr(robot, 'robot_type', 'unknown')
        battery_level = getattr(robot, 'battery_level', 100.0)
        
        # Get compatible tasks
        compatible_task_types = self.task_registry.get_compatible_tasks(
            robot_capabilities, robot_type, battery_level
        )
        
        # Build response with task details
        compatible_tasks = {}
        for task_type in compatible_task_types:
            capability = self.task_registry.get_capability(task_type)
            if capability:
                compatible_tasks[task_type] = {
                    "description": capability.description,
                    "category": capability.category,
                    "required_capabilities": capability.required_robot_capabilities,
                    "min_battery_level": capability.min_battery_level,
                    "payload_requirements": capability.payload_requirements
                }
        
        return {
            "robot_id": robot_id,
            "robot_type": robot_type,
            "robot_capabilities": robot_capabilities,
            "battery_level": battery_level,
            "compatible_tasks": compatible_tasks,
            "total_available": len(compatible_task_types)
        }
    
    def list_all_tasks(self) -> Dict[str, Any]:
        """
        List all available tasks with their capabilities.
        
        Returns:
            Dict with all task types organized by category
        """
        all_tasks = {}
        
        # Get all task capabilities
        for task_type in self.task_registry.list_tasks():
            capability = self.task_registry.get_capability(task_type)
            if capability:
                category = capability.category
                if category not in all_tasks:
                    all_tasks[category] = {}
                
                all_tasks[category][task_type] = {
                    "description": capability.description,
                    "required_capabilities": capability.required_robot_capabilities,
                    "required_robot_types": capability.required_robot_types,
                    "min_battery_level": capability.min_battery_level,
                    "payload_requirements": capability.payload_requirements
                }
        
        return {
            "tasks": all_tasks,
            "total_types": len(self.task_registry.list_tasks()),
            "categories": list(all_tasks.keys())
        }
    
    def estimate_task_duration(self, task_type: str, task_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate task execution duration.
        
        Returns:
            Dict with duration estimate and details
        """
        executor = self.task_registry.get_executor(task_type)
        if not executor:
            return {"error": f"Unknown task type: {task_type}"}
        
        duration = executor.estimate_duration(task_spec)
        return {
            "task_type": task_type,
            "estimated_duration_minutes": duration,
            "spec_used": task_spec
        }


# Global dynamic executor instance
dynamic_executor = DynamicTaskExecutor()


def run_dynamic_task(
    controller: FleetController,
    robot_id: str,
    task_id: str,
    task_spec: Dict[str, Any],
    *,
    projector: Optional[LocalTwinProjector] = None,
    sink: Optional[InMemoryEventSink] = None,
) -> Dict[str, Any]:
    """
    Convenience function to run a task using the dynamic executor.
    
    This replaces the old run_single_task function.
    """
    return dynamic_executor.execute_task(
        controller, robot_id, task_id, task_spec,
        projector=projector, sink=sink
    )


def get_robot_compatible_tasks(robot_id: str, controller: FleetController) -> Dict[str, Any]:
    """
    Get tasks compatible with a robot.
    
    This replaces hardcoded task compatibility checks.
    """
    return dynamic_executor.get_compatible_tasks(robot_id, controller)


def generate_dynamic_task_specs(controller: FleetController, robot_ids: list[str]) -> list[dict]:
    """
    Generate dynamic task specifications based on available robot capabilities.
    
    This replaces the hardcoded DEFAULT_TASK_SPECS.
    """
    task_specs = []
    
    for robot_id in robot_ids:
        robot = controller.get_robot(robot_id)
        if not robot:
            continue
            
        # Get compatible tasks for this robot
        compatible_tasks = get_robot_compatible_tasks(robot_id, controller)
        
        if "error" in compatible_tasks:
            continue
            
        # Generate a sample task for each category
        categories = compatible_tasks.get("compatible_tasks", {}).keys()
        
        for category in list(categories)[:2]:  # Limit to 2 tasks per robot
            if category == "navigation":
                task_specs.append({
                    "robot_id": robot_id,
                    "type": "navigate_to",
                    "target_type": "coordinates",
                    "target": {"x": 1.0, "y": 0.5}
                })
            elif category == "manipulation":
                task_specs.append({
                    "robot_id": robot_id,
                    "type": "scan",
                    "scan_type": "qr",
                    "duration": 3.0
                })
            elif category == "transport":
                task_specs.append({
                    "robot_id": robot_id,
                    "type": "transport",
                    "source_zone": "storage",
                    "destination_zone": "delivery",
                    "payload_weight_kg": 2.0
                })
    
    return task_specs


def list_available_tasks() -> Dict[str, Any]:
    """
    List all available tasks.
    
    This replaces hardcoded task constants.
    """
    return dynamic_executor.list_all_tasks()


def estimate_task_execution(task_type: str, task_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Estimate task execution time.
    
    This provides planning capabilities for the mission brain.
    """
    return dynamic_executor.estimate_task_duration(task_type, task_spec)


def run_dynamic_pilot(
    num_robots: int = 2,
    sim: bool = True,
    task_specs: list[dict] | None = None,
    host_template: str = "192.168.1.{}",  # e.g. 192.168.1.101, 192.168.1.102
    *,
    domain_id: int = 0,
    interface: str = "",
) -> dict:
    """
    Run pilot using dynamic task registry instead of hardcoded tasks.
    
    Args:
        num_robots: Number of robots to initialize
        sim: Use simulation mode
        task_specs: List of task specifications (from mission planner or defaults)
        host_template: Template for robot IP addresses
        domain_id: DDS domain ID
        interface: Network interface for DDS
        
    Returns:
        Summary dict with execution results
    """
    # Initialize controller
    controller = FleetController()
    robot_ids = [f"r1_{i+1}" for i in range(num_robots)]

    # Initialize robots via SDK wrapper and register with controller
    for i, rid in enumerate(robot_ids):
        host = host_template.format(101 + i) if "{}" in host_template else host_template
        manager = RobotManager(
            robot_id=rid,
            host=host,
            sim=sim,
            domain_id=domain_id,
            interface=interface or None,
        )
        if not manager.connect():
            return {
                "success": False,
                "error": f"Failed to connect robot {rid}",
                "robot_results": {},
            }
        controller.register_robot(rid, robot_manager=manager)

    # Use provided task specs or generate dynamic ones
    if not task_specs:
        task_specs = generate_dynamic_task_specs(controller, robot_ids)

    # Execute tasks using dynamic system
    results_by_robot: dict[str, list[dict]] = {rid: [] for rid in robot_ids}
    errors: list[str] = []

    print(f"Executing {len(task_specs)} tasks using dynamic task registry...")
    print(f"Available task types: {task_registry.list_tasks()}")
    if task_specs:
        print(f"Task specs to execute: {task_specs}")

    for idx, spec in enumerate(task_specs):
        robot_id = spec.get("robot_id", robot_ids[idx % num_robots])
        task_id = f"task_{idx}_{spec.get('type', 'unknown')}"
        
        # Log task assignment
        controller.assign_task(task_id, robot_id, spec)
        
        # Execute using dynamic system
        result = run_dynamic_task(controller, robot_id, task_id, spec)
        results_by_robot[robot_id].append({"task_id": task_id, "spec": spec, "result": result})

        if not result.get("success"):
            errors.append(f"{robot_id}: {task_id} -> {result.get('error', result)}")

    fleet_status = controller.get_fleet_status()

    return {
        "success": len(errors) == 0,
        "robot_results": results_by_robot,
        "fleet_status_final": fleet_status,
        "errors": errors,
        "sim": sim,
        "domain_id": domain_id,
        "interface": interface,
        "task_system": "dynamic_registry",
        "total_tasks_executed": len(task_specs)
    }


def show_task_capabilities():
    """Display all available task types and their capabilities."""
    tasks_info = list_available_tasks()
    
    print("\\n=== Dynamic Task Registry ===")
    print(f"Total task types: {tasks_info['total_types']}")
    print(f"Categories: {', '.join(tasks_info['categories'])}")
    
    for category, task_types in tasks_info['tasks'].items():
        print(f"\\n--- {category.upper()} ---")
        for task_type, info in task_types.items():
            print(f"  {task_type}: {info['description']}")
            print(f"    Required capabilities: {', '.join(info['required_capabilities'])}")
            if info.get('min_battery_level', 0) > 0:
                print(f"    Min battery level: {info['min_battery_level']}%")


def main() -> int:
    print("DEBUG: Main function started", flush=True)
    parser = argparse.ArgumentParser(description="Run dynamic fleet pilot (1–2 robots)")
    parser.add_argument("--sim", action="store_true", help="Stub simulation (no SDK, no hardware)")
    parser.add_argument("--mujoco", action="store_true", help="Use SDK with MuJoCo sim (domain_id=1, interface=lo)")
    parser.add_argument("--interface", type=str, default="", help="Network interface for real robot")
    parser.add_argument("--robots", type=int, default=2, choices=(1, 2), help="Number of robots")
    parser.add_argument("--tasks", type=str, default="", help="Comma-separated task types (e.g., navigate_to,scan)")
    parser.add_argument("--list-tasks", action="store_true", help="List all available task types")
    parser.add_argument("--show-capabilities", action="store_true", help="Show task capability details")
    args = parser.parse_args()
    print(f"DEBUG: Parsed args: {args}", flush=True)

    # Show task information and exit
    if args.list_tasks:
        show_task_capabilities()
        return 0
    
    if args.show_capabilities:
        show_task_capabilities()
        return 0

    # Parse task arguments
    task_specs = None
    if args.tasks:
        task_types = [t.strip() for t in args.tasks.split(",")]
        task_specs = []
        for t in task_types:
            if t == "scan":
                task_specs.append({
                    "type": "scan",
                    "scan_type": "qr",
                    "duration": 3.0
                })
            elif t == "navigate_to":
                task_specs.append({
                    "type": "navigate_to",
                    "target_type": "coordinates",
                    "target": {"x": 1.0, "y": 0.5}
                })
            else:
                task_specs.append({"type": t})
        print(f"DEBUG: Parsed task types from command line: {task_types}", flush=True)
        print(f"DEBUG: Generated task specs: {task_specs}", flush=True)
        print(f"DEBUG: Final task_specs value: {task_specs}", flush=True)

    # Configure simulation/SDK settings
    sim = args.sim
    domain_id = 0
    interface = args.interface or ""
    
    if args.sim:
        pass  # stub only
    elif args.mujoco:
        sim = False
        domain_id = 1
        interface = "lo0"
        if not sdk_available():
            print("unitree_sdk2_python not installed. See SDK/README.md.")
            return 1
    elif args.interface:
        sim = False
        if not sdk_available():
            print("unitree_sdk2_python not installed. See SDK/README.md.")
            return 1
    elif sdk_available():
        # Default to MuJoCo when SDK is installed
        sim = False
        domain_id = 1
        interface = "lo0"
    else:
        if args.mujoco or args.interface:
            print("unitree_sdk2_python not installed. Install from SDK/unitree_sdk2_python.")
        else:
            print("No SDK installed. Use --sim for stub, or install unitree_sdk2_python.")
        return 1

    # Run dynamic pilot
    summary = run_dynamic_pilot(
        num_robots=args.robots,
        sim=sim,
        task_specs=task_specs,
        domain_id=domain_id,
        interface=interface,
    )
    
    print("\\n=== Dynamic Pilot Results ===")
    print(f"Success: {summary['success']}")
    print(f"Tasks executed: {summary['total_tasks_executed']}")
    print(f"Task system: {summary['task_system']}")
    
    if summary.get("error"):
        print(f"Error: {summary['error']}")
    if summary.get("errors"):
        print("Errors:")
        for error in summary["errors"]:
            print(f"  - {error}")
    
    print(f"Logs written to: {log_utils.get_log_dir()}")
    return 0 if summary["success"] else 1


if __name__ == "__main__":
    exit(main())
