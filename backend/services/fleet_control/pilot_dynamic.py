"""
Dynamic pilot module that replaces hardcoded tasks with the task registry system.

This module provides the main pilot loop interface but uses the dynamic
task execution system instead of hardcoded task constants.
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Ensure project root is on path for data.log_utils
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from data import log_utils
from fleet_control.controller import FleetController
from fleet_control.dynamic_pilot import run_dynamic_task, get_robot_compatible_tasks
from fleet_control.edge_bridge import InMemoryEventSink
from fleet_control.mock_twin import LocalTwinProjector
from fleet_control.robot_manager import RobotManager, sdk_available
from fleet_control.task_registry import task_registry


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


def show_task_capabilities():
    """Display all available task types and their capabilities."""
    from fleet_control.dynamic_pilot import list_available_tasks
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


def is_simulation() -> bool:
    """Return True if running in simulation."""
    return "--sim" in sys.argv or "SIMULATION=1" in str(os.environ.get("SIMULATION", ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run dynamic fleet pilot (1–2 robots)")
    parser.add_argument("--sim", action="store_true", help="Stub simulation (no SDK, no hardware)")
    parser.add_argument("--mujoco", action="store_true", help="Use SDK with MuJoCo sim (domain_id=1, interface=lo)")
    parser.add_argument("--interface", type=str, default="", help="Network interface for real robot")
    parser.add_argument("--robots", type=int, default=2, choices=(1, 2), help="Number of robots")
    parser.add_argument("--tasks", type=str, default="", help="Comma-separated task types (e.g., navigate_to,scan)")
    parser.add_argument("--list-tasks", action="store_true", help="List all available task types")
    parser.add_argument("--show-capabilities", action="store_true", help="Show task capability details")
    args = parser.parse_args()

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
        task_specs = [{"type": t} for t in task_types]

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
