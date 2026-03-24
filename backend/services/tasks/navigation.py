"""
Navigation task implementations for the dynamic task registry.

This module provides navigation-specific tasks like walking, turning, and path following.
"""

from fleet_control.task_registry import TaskExecutor, TaskCapability, register_task_executor
from fleet_control.robot_manager import RobotManager
from typing import Dict, Any
import time


class WalkForwardExecutor(TaskExecutor):
    """Execute walk forward tasks."""
    
    def execute(self, robot: RobotManager, spec: Dict[str, Any]) -> Dict[str, Any]:
        meters = spec.get("meters", 1.0)
        if meters <= 0:
            return {"success": True, "meters": 0}
        
        # Use robot's walk_forward method
        success = robot.walk_forward(meters)
        return {"success": success, "meters": meters}
    
    def estimate_duration(self, spec: Dict[str, Any]) -> float:
        meters = spec.get("meters", 1.0)
        # Assume 0.5 m/s walking speed
        return max(0.5, meters / 0.5)


class TurnExecutor(TaskExecutor):
    """Execute turn in place tasks."""
    
    def execute(self, robot: RobotManager, spec: Dict[str, Any]) -> Dict[str, Any]:
        degrees = spec.get("degrees", 90)
        if abs(degrees) < 1:
            return {"success": True, "degrees": 0}
        
        success = robot.turn(degrees)
        return {"success": success, "degrees": degrees}
    
    def estimate_duration(self, spec: Dict[str, Any]) -> float:
        degrees = spec.get("degrees", 90)
        # Assume 90 degrees/second turning speed
        return max(0.3, abs(degrees) / 90)


class NavigateToExecutor(TaskExecutor):
    """Navigate to a specific location or zone."""
    
    def execute(self, robot: RobotManager, spec: Dict[str, Any]) -> Dict[str, Any]:
        target = spec.get("target")
        target_type = spec.get("target_type", "coordinates")
        
        if not target:
            return {"success": False, "error": "No target specified"}
        
        if target_type == "coordinates":
            return self._navigate_to_coordinates(robot, target)
        elif target_type == "zone":
            return self._navigate_to_zone(robot, target)
        else:
            return {"success": False, "error": f"Unknown target type: {target_type}"}
    
    def _navigate_to_coordinates(self, robot: RobotManager, target: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to specific x,y coordinates."""
        x = target.get("x", 0)
        y = target.get("y", 0)
        
        # Get current position
        current_pos = getattr(robot, 'get_position', lambda: {"x": 0, "y": 0})()
        dx = x - current_pos.get("x", 0)
        dy = y - current_pos.get("y", 0)
        
        # Calculate distance and bearing
        distance = (dx**2 + dy**2)**0.5
        bearing = 0  # Simplified - would need atan2 for real implementation
        
        # Turn to face target
        turn_success = robot.turn(bearing)
        if not turn_success:
            return {"success": False, "error": "Failed to turn toward target"}
        
        # Walk to target
        walk_success = robot.walk_forward(distance)
        return {
            "success": walk_success,
            "target": {"x": x, "y": y},
            "distance_traveled": distance,
            "starting_position": current_pos
        }
    
    def _navigate_to_zone(self, robot: RobotManager, zone_name: str) -> Dict[str, Any]:
        """Navigate to a named zone."""
        # This would integrate with zone mapping system
        # For now, simulate zone navigation
        zone_positions = {
            "kitchen": {"x": 2, "y": 1},
            "living_room": {"x": 0, "y": 0},
            "bedroom": {"x": -1, "y": 2},
            "entrance": {"x": 0, "y": -2}
        }
        
        target_pos = zone_positions.get(zone_name.lower())
        if not target_pos:
            return {"success": False, "error": f"Unknown zone: {zone_name}"}
        
        return self._navigate_to_coordinates(robot, target_pos)
    
    def estimate_duration(self, spec: Dict[str, Any]) -> float:
        target_type = spec.get("target_type", "coordinates")
        if target_type == "coordinates":
            target = spec.get("target", {})
            x, y = target.get("x", 0), target.get("y", 0)
            # Estimate based on distance from origin
            distance = (x**2 + y**2)**0.5
            return max(1.0, distance / 0.5)
        else:
            # Zone navigation - estimate 2-5 minutes
            return 3.0


# Register navigation tasks
register_task_executor(
    "walk_forward",
    TaskCapability(
        task_type="walk_forward",
        required_robot_capabilities=["mobility"],
        description="Walk forward a specified distance",
        category="navigation"
    )
)

register_task_executor(
    "turn",
    TaskCapability(
        task_type="turn", 
        required_robot_capabilities=["mobility"],
        description="Turn in place by specified degrees",
        category="navigation"
    )
)

register_task_executor(
    "navigate_to",
    TaskCapability(
        task_type="navigate_to",
        required_robot_capabilities=["mobility", "navigation"],
        description="Navigate to specific coordinates or zone",
        category="navigation"
    )
)
