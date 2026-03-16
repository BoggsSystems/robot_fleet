"""
Shared helpers for high-level tasks.

Provides navigation and logging utilities used by inventory_scan, restock, etc.
All tasks accept a RobotManager instance (caller obtains it from FleetController).
"""

import math
import time
from typing import Any, Callable, TypeVar

# Type for robot manager (avoid circular import by using Any or a protocol later)
RobotManagerT = TypeVar("RobotManagerT")


def navigate_to(robot: Any, target_x: float, target_y: float) -> bool:
    """
    Move robot to global position (target_x, target_y) in the warehouse.
    Uses current position from RobotManager.get_status()["pose"].
    
    Implements a basic waypoint path planner to avoid the two central shelves
    located at x=-2.0 and x=2.0.
    """
    status = robot.get_status()
    pose = status.get("pose", {"x": 0.0, "y": 0.0, "theta": 0.0})
    curr_x, curr_y = pose["x"], pose["y"]
    
    # Very basic static obstacle avoidance for our specific warehouse.xml
    # Shelves are at x=-2.0 and x=2.0, extending from y=-1.5 to y=1.5
    waypoints = []
    
    # If crossing the shelf line (y=0) from far negative/positive Y
    if abs(curr_y) > 2.0 and abs(target_y) < 2.0:
        # Route through the center aisle (x=0) to be safe
        waypoints.append((0.0, curr_y))
        waypoints.append((0.0, target_y))
        
    waypoints.append((target_x, target_y))
    
    for wx, wy in waypoints:
        # Re-fetch pose in case of drift
        pose = robot.get_status().get("pose", {"x": 0.0, "y": 0.0, "theta": 0.0})
        cx, cy, ctheta = pose["x"], pose["y"], pose["theta"]
        
        dx = wx - cx
        dy = wy - cy
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 0.1:
            continue
            
        target_heading_rad = math.atan2(dy, dx)
        target_heading_deg = math.degrees(target_heading_rad)
        
        # Calculate optimal turn direction
        turn_diff = (target_heading_deg - ctheta + 180) % 360 - 180
        
        # 1. Turn to face waypoint
        if abs(turn_diff) > 5.0:
            ok = robot.turn(turn_diff)
            if not ok:
                return False
                
        # 2. Walk to waypoint
        ok = robot.walk_forward(distance)
        if not ok:
            return False
            
    return True


def do_scan(robot: Any, target: str = "inventory") -> dict:
    """
    Perform a single scan at current location (vision/QR/inventory placeholder).
    Returns dict with success, scanned id/count, raw data if any.
    TODO: Use robot.get_sensor_data("camera") and decode QR / run detector.
    """
    _ = target
    sensor = robot.get_sensor_data("camera")
    time.sleep(0.25)
    return {"success": True, "scanned": "placeholder", "data": sensor.get("data"), "sensor": sensor}


def do_pick(robot: Any, source: dict) -> bool:
    """
    Pick item(s) from source location (placeholder: no arm/gripper SDK yet).
    TODO: Integrate arm/gripper commands when available.
    """
    _ = source
    time.sleep(0.2)
    return True


def do_place(robot: Any, target: dict) -> bool:
    """
    Place carried item at target location (placeholder).
    TODO: Integrate arm/gripper commands when available.
    """
    _ = target
    time.sleep(0.2)
    return True


def run_with_logging(
    task_id: str,
    robot_id: str,
    spec: dict,
    fn: Callable[[], dict],
) -> dict:
    """
    Run a callable that returns a result dict; log task start/end and duration.
    Uses data.log_utils. Returns the result from fn().
    """
    import sys
    from pathlib import Path
    _root = Path(__file__).resolve().parents[1]
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    from data import log_utils
    start = time.perf_counter()
    log_utils.log_task_start(task_id, robot_id, spec)
    try:
        result = fn()
    except Exception as e:
        result = {"success": False, "errors": [str(e)]}
    duration = time.perf_counter() - start
    log_utils.log_task_end(task_id, robot_id, result, duration)
    return result
