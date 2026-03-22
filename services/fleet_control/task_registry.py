"""
Dynamic task registry system for fleet control.

Replaces hardcoded task constants with a pluggable architecture
that allows tasks to be registered dynamically and executed based on task_type.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, Callable
from dataclasses import dataclass
import importlib
import inspect
import logging

from .robot_manager import RobotManager


logger = logging.getLogger(__name__)


@dataclass
class TaskCapability:
    """Defines requirements and capabilities for a task type."""
    task_type: str
    required_robot_capabilities: List[str]
    optional_robot_capabilities: List[str] = None
    required_robot_types: List[str] = None
    min_battery_level: float = 0.0
    payload_requirements: Dict[str, Any] = None
    description: str = ""
    category: str = "general"  # navigation, manipulation, transport, etc.


class TaskExecutor(ABC):
    """Base class for task executors."""
    
    def __init__(self, task_type: str):
        self.task_type = task_type
    
    @abstractmethod
    def execute(self, robot: RobotManager, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the task on the given robot.
        
        Args:
            robot: RobotManager instance to control
            spec: Task specification with parameters
            
        Returns:
            Dict with success status and results
        """
        pass
    
    def validate_spec(self, spec: Dict[str, Any]) -> bool:
        """Validate task specification before execution."""
        return True
    
    def estimate_duration(self, spec: Dict[str, Any]) -> float:
        """Estimate task duration in minutes."""
        return 1.0  # Default 1 minute


class TaskRegistry:
    """Registry for dynamic task management."""
    
    def __init__(self):
        self._executors: Dict[str, TaskExecutor] = {}
        self._capabilities: Dict[str, TaskCapability] = {}
        self._loaded_modules: set = set()
    
    def register_task(
        self,
        task_type: str,
        executor_class: Type[TaskExecutor],
        capability: TaskCapability
    ) -> None:
        """Register a new task type."""
        executor = executor_class(task_type)
        self._executors[task_type] = executor
        self._capabilities[task_type] = capability
        logger.info(f"Registered task type: {task_type}")
    
    def register_executor(self, task_type: str, executor: TaskExecutor, capability: TaskCapability) -> None:
        """Register an executor instance."""
        self._executors[task_type] = executor
        self._capabilities[task_type] = capability
        logger.info(f"Registered executor for: {task_type}")
    
    def get_executor(self, task_type: str) -> TaskExecutor | None:
        """Get executor for a task type."""
        return self._executors.get(task_type)
    
    def get_capability(self, task_type: str) -> TaskCapability | None:
        """Get capability requirements for a task type."""
        return self._capabilities.get(task_type)
    
    def list_tasks(self) -> List[str]:
        """List all registered task types."""
        return list(self._executors.keys())
    
    def list_tasks_by_category(self, category: str) -> List[str]:
        """List tasks by category."""
        return [
            task_type for task_type, capability in self._capabilities.items()
            if capability.category == category
        ]
    
    def get_compatible_tasks(
        self, 
        robot_capabilities: List[str], 
        robot_type: str = None,
        battery_level: float = 100.0
    ) -> List[str]:
        """Get tasks compatible with given robot capabilities."""
        compatible_tasks = []
        
        for task_type, capability in self._capabilities.items():
            # Check required capabilities
            has_required = all(
                cap in robot_capabilities 
                for cap in capability.required_robot_capabilities
            )
            
            # Check robot type compatibility
            type_compatible = (
                not capability.required_robot_types or
                robot_type in capability.required_robot_types
            )
            
            # Check battery level
            battery_ok = battery_level >= capability.min_battery_level
            
            if has_required and type_compatible and battery_ok:
                compatible_tasks.append(task_type)
        
        return compatible_tasks
    
    def load_tasks_from_module(self, module_path: str) -> None:
        """Dynamically load tasks from a module."""
        try:
            if module_path in self._loaded_modules:
                return
                
            module = importlib.import_module(module_path)
            self._loaded_modules.add(module_path)
            
            # Look for task classes in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (hasattr(obj, 'TASK_TYPE') and 
                    hasattr(obj, 'TASK_CAPABILITY') and
                    issubclass(obj, TaskExecutor)):
                    
                    task_type = getattr(obj, 'TASK_TYPE')
                    capability = getattr(obj, 'TASK_CAPABILITY')
                    self.register_task(task_type, obj, capability)
                    
        except Exception as e:
            logger.error(f"Failed to load tasks from {module_path}: {e}")
    
    def auto_discover_tasks(self) -> None:
        """Auto-discover task modules."""
        # Try to load common task modules
        task_modules = [
            'tasks.navigation',
            'tasks.manipulation', 
            'tasks.transport',
            'tasks.inspection',
            'tasks.safety'
        ]
        
        for module in task_modules:
            try:
                self.load_tasks_from_module(module)
            except ImportError:
                # Module doesn't exist, that's ok
                pass


# Global task registry instance
task_registry = TaskRegistry()


def register_task_executor(task_type: str, capability: TaskCapability):
    """Decorator for registering task executors."""
    def decorator(cls: Type[TaskExecutor]):
        task_registry.register_task(task_type, cls, capability)
        return cls
    return decorator


# Built-in basic task executors for common operations
class NavigateExecutor(TaskExecutor):
    """Basic navigation task executor."""
    
    def execute(self, robot: RobotManager, spec: Dict[str, Any]) -> Dict[str, Any]:
        action = spec.get("action", "walk_forward")
        
        if action == "walk_forward":
            meters = spec.get("meters", 1.0)
            success = robot.walk_forward(meters)
            return {"success": success, "meters": meters, "action": action}
        elif action == "turn":
            degrees = spec.get("degrees", 90)
            success = robot.turn(degrees)
            return {"success": success, "degrees": degrees, "action": action}
        else:
            return {"success": False, "error": f"Unknown navigation action: {action}"}
    
    def estimate_duration(self, spec: Dict[str, Any]) -> float:
        action = spec.get("action", "walk_forward")
        if action == "walk_forward":
            meters = spec.get("meters", 1.0)
            return max(0.5, meters / 0.5)  # 0.5 m/s walking speed
        elif action == "turn":
            degrees = spec.get("degrees", 90)
            return max(0.3, abs(degrees) / 90)  # 90 deg/s turning speed
        return 1.0


class ManipulationExecutor(TaskExecutor):
    """Basic manipulation task executor."""
    
    def execute(self, robot: RobotManager, spec: Dict[str, Any]) -> Dict[str, Any]:
        action = spec.get("action", "grasp")
        
        if not robot.supports_arm_actions():
            return {"success": False, "error": "Robot does not support arm actions"}
        
        if action == "grasp":
            target = spec.get("target", "object")
            success = robot.perform_action(f"grasp_{target}")
            return {"success": success, "target": target, "action": action}
        elif action == "release":
            success = robot.perform_action("release_arm")
            return {"success": success, "action": action}
        elif action == "scan":
            scan_type = spec.get("scan_type", "qr")
            if scan_type == "qr":
                # Simulate QR scanning
                import time
                time.sleep(0.5)
                return {"success": True, "scanned": "placeholder_qr", "action": action}
            else:
                return {"success": False, "error": f"Unsupported scan type: {scan_type}"}
        else:
            return {"success": False, "error": f"Unknown manipulation action: {action}"}
    
    def validate_spec(self, spec: Dict[str, Any]) -> bool:
        action = spec.get("action")
        return action in ["grasp", "release", "scan"]


class TransportExecutor(TaskExecutor):
    """Transport task executor for moving items."""
    
    def execute(self, robot: RobotManager, spec: Dict[str, Any]) -> Dict[str, Any]:
        source = spec.get("source_zone")
        destination = spec.get("destination_zone")
        payload = spec.get("payload_weight_kg", 0)
        
        # Check payload capacity
        max_payload = getattr(robot, 'max_payload_kg', 10.0)
        if payload > max_payload:
            return {
                "success": False, 
                "error": f"Payload {payload}kg exceeds max {max_payload}kg"
            }
        
        # Navigate to source
        if source:
            success = robot.walk_forward(0.5)  # Approach source
            if not success:
                return {"success": False, "error": "Failed to approach source"}
        
        # Simulate loading
        import time
        time.sleep(1.0)
        
        # Navigate to destination  
        if destination:
            success = robot.walk_forward(2.0)  # Move to destination
            if not success:
                return {"success": False, "error": "Failed to reach destination"}
        
        return {
            "success": True,
            "source_zone": source,
            "destination_zone": destination,
            "payload_weight_kg": payload,
            "transport_complete": True
        }
    
    def estimate_duration(self, spec: Dict[str, Any]) -> float:
        # Estimate based on distance and payload
        return 3.0  # 3 minutes average transport time


# Register built-in executors
task_registry.register_task(
    "walk_forward",
    NavigateExecutor,
    TaskCapability(
        task_type="walk_forward",
        required_robot_capabilities=["mobility"],
        description="Navigation tasks (walk, turn, etc.)",
        category="navigation"
    )
)

task_registry.register_task(
    "navigate_to",
    NavigateExecutor,
    TaskCapability(
        task_type="navigate_to",
        required_robot_capabilities=["mobility", "navigation"],
        description="Navigate to specific coordinates or zone",
        category="navigation"
    )
)

task_registry.register_task(
    "scan",
    ManipulationExecutor,
    TaskCapability(
        task_type="scan",
        required_robot_capabilities=["camera", "processing"],
        description="Scan QR codes, barcodes, or perform visual detection",
        category="manipulation"
    )
)

task_registry.register_task(
    "manipulate", 
    ManipulationExecutor,
    TaskCapability(
        task_type="manipulate",
        required_robot_capabilities=["arm_control", "gripper"],
        description="Manipulation tasks (grasp, release, scan)",
        category="manipulation"
    )
)

task_registry.register_task(
    "transport",
    TransportExecutor,
    TaskCapability(
        task_type="transport",
        required_robot_capabilities=["mobility", "cargo"],
        required_robot_types=["cargo_robot", "humanoid"],
        min_battery_level=20.0,
        payload_requirements={"max_weight_kg": 50.0},
        description="Transport items between zones",
        category="transport"
    )
)
