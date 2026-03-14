"""
Sample task: restocking.

Robot picks items from a source location (e.g. back room, pallet) and
places them at target locations (shelves, bins) for warehouse/retail restocking.
"""

# TODO: Import robot interface and task base
# from fleet_control.robot_manager import RobotManager
# from .base import BaseTask  # if you add a base class


def run_restock(robot_id: str, source: dict, targets: list, **kwargs) -> dict:
    """
    Execute restock: pick from source, place at each target.

    Args:
        robot_id: Id of the robot to use.
        source: Source location (e.g. {"location_id": "...", "item_sku": "..."}).
        targets: List of target locations and quantities.
        **kwargs: Optional (e.g. priority, max_items).

    Returns:
        Result dict with success, items_restocked, and any errors.
    """
    # TODO: Get robot; navigate to source; pick; navigate to each target; place; log
    return {"success": False, "items_restocked": 0, "errors": ["Not implemented"]}


# AI extension point: Add pick/place primitives, motion commands for arm/gripper,
# and multi-robot coordination (e.g. split targets across robots).
