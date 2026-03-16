"""
Run high-level tasks (inventory_scan, restock) from the CLI.

Uses one robot from the fleet (stub or SDK). Example:
  python -m tasks.run_tasks --sim inventory_scan
  python -m tasks.run_tasks --sim restock
  python -m tasks.run_tasks --mujoco inventory_scan
"""

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from data import log_utils
from fleet_control.controller import FleetController
from fleet_control.robot_manager import RobotManager, sdk_available
from tasks.inventory_scan import run_inventory_scan
from tasks.restock import run_restock


def _parse_args():
    p = argparse.ArgumentParser(description="Run inventory_scan or restock task")
    p.add_argument("task", choices=["inventory_scan", "restock"], help="Task to run")
    p.add_argument("--sim", action="store_true", help="Use stub robot")
    p.add_argument("--mujoco", action="store_true", help="Use SDK + MuJoCo (domain 1, lo)")
    p.add_argument("--interface", type=str, default="", help="NIC for real robot (e.g. enp2s0)")
    return p.parse_args()


def main():
    args = _parse_args()
    sim = args.sim
    domain_id = 0
    interface = ""
    if args.mujoco:
        if not sdk_available():
            print("SDK not installed. Use --sim or install unitree_sdk2_python.")
            return 1
        sim = False
        domain_id = 1
        interface = "lo"
    elif args.interface:
        if not sdk_available():
            print("SDK not installed.")
            return 1
        sim = False
        interface = args.interface

    controller = FleetController()
    robot_id = "r1_1"
    manager = RobotManager(robot_id=robot_id, sim=sim, domain_id=domain_id, interface=interface or None)
    if not manager.connect():
        print("Failed to connect robot")
        return 1
    controller.register_robot(robot_id, robot_manager=manager)

    task_id = f"run_tasks_{args.task}"
    log_utils.log_task_start(task_id, robot_id, {"task": args.task})
    start = __import__("time").perf_counter()

    if args.task == "inventory_scan":
        zones = [{"zone_id": "A1", "x": 1.0, "y": 0}, {"zone_id": "A2", "x": 0.5, "y": 0.5}]
        result = run_inventory_scan(manager, zones, robot_id=robot_id)
    else:
        source = {"location_id": "pallet_1", "x": 0.5, "y": 0}
        targets = [
            {"location_id": "shelf_1", "x": 1.0, "y": 0, "quantity": 2},
            {"location_id": "shelf_2", "x": 1.0, "y": 0.5, "quantity": 1},
        ]
        result = run_restock(manager, source, targets, robot_id=robot_id)

    duration = __import__("time").perf_counter() - start
    log_utils.log_task_end(task_id, robot_id, result, duration)
    print("Success:", result.get("success"))
    print("Result:", result)
    print("Logs:", log_utils.get_log_dir())
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
