"""
Restocking task.

Robot picks items from a source location and places them at target locations
(shelves, bins). Placeholder pick/place until arm/gripper SDK is available.
"""

from typing import Any

from .base import do_pick, do_place, navigate_to


def run_restock(
    robot: Any,
    source: dict,
    targets: list[dict],
    *,
    robot_id: str = "",
    max_items: int | None = None,
    **kwargs: Any,
) -> dict:
    """
    Execute restock: navigate to source, pick, then for each target navigate and place.

    Args:
        robot: RobotManager instance (from FleetController.get_robot).
        source: Source location, e.g. {"location_id": "pallet_1", "x": 0, "y": 0}.
                x,y in meters for navigation.
        targets: List of target specs, e.g. [{"location_id": "shelf_A1", "x": 2, "y": 1, "quantity": 3}].
        robot_id: Optional robot id for logging (caller may pass for logging).
        max_items: Optional cap on total items to restock (default: sum of quantities).
        **kwargs: Ignored; for future options (priority, etc.).

    Returns:
        Result dict with success, items_restocked, and any errors.
    """
    _ = robot_id, kwargs
    errors: list[str] = []
    items_restocked = 0
    src_id = source.get("location_id", "source")
    x_src = source.get("x", 0.0)
    y_src = source.get("y", 0.0)

    ok = navigate_to(robot, x_src, y_src)
    if not ok:
        return {"success": False, "items_restocked": 0, "errors": [f"{src_id}: navigation failed"]}
    ok = do_pick(robot, source)
    if not ok:
        return {"success": False, "items_restocked": 0, "errors": [f"{src_id}: pick failed"]}

    total_requested = sum(t.get("quantity", 1) for t in targets)
    limit = total_requested if max_items is None else min(max_items, total_requested)

    for target in targets:
        if items_restocked >= limit:
            break
        loc_id = target.get("location_id", "target")
        qty = min(target.get("quantity", 1), limit - items_restocked)
        x_t = target.get("x", 0.0)
        y_t = target.get("y", 0.0)
        ok = navigate_to(robot, x_t, y_t)
        if not ok:
            errors.append(f"{loc_id}: navigation failed")
            continue
        ok = do_place(robot, target)
        if not ok:
            errors.append(f"{loc_id}: place failed")
            continue
        items_restocked += qty

    return {
        "success": len(errors) == 0,
        "items_restocked": items_restocked,
        "errors": errors,
        "source": src_id,
        "target_count": len(targets),
    }


# AI extension point: Add pick_n(robot, source, n), place_n(robot, target, n),
# and multi-robot split (assign subset of targets per robot).
