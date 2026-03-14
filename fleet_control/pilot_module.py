"""
First working pilot module for 1–2 Unitree R1 robots.

Initializes robots via SDK wrapper (robot_manager), assigns simple tasks
(walk 2 m, turn 90°, scan QR placeholder, report to dashboard placeholder),
coordinates multi-robot execution with alternating assignment, and logs
all task execution to data/logs/. Simulation-ready via sim=True.

Run: python -m fleet_control.pilot_module [--sim] [--robots 2]
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Ensure project root is on path for data.log_utils
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from data import log_utils
from fleet_control.controller import FleetController
from fleet_control.robot_manager import RobotManager, sdk_available

# -----------------------------------------------------------------------------
# Task type constants (AI can extend with new task types)
# -----------------------------------------------------------------------------
TASK_WALK_FORWARD = "walk_forward"
TASK_TURN = "turn"
TASK_SCAN_QR = "scan_qr"
TASK_REPORT_DASHBOARD = "report_dashboard"

# Default pilot task sequence for each robot
DEFAULT_TASK_SPECS = [
    {"type": TASK_WALK_FORWARD, "params": {"meters": 2.0}},
    {"type": TASK_TURN, "params": {"degrees": 90}},
    {"type": TASK_SCAN_QR, "params": {"target": "inventory_item_placeholder"}},
    {"type": TASK_REPORT_DASHBOARD, "params": {}},
]


# -----------------------------------------------------------------------------
# Task execution (uses robot_manager wrapper; TODOs for real motion/sensors)
# -----------------------------------------------------------------------------


def run_walk_forward(robot: RobotManager, spec: dict) -> dict:
    """Execute walk forward N meters. Uses robot_manager.walk_forward()."""
    meters = spec.get("params", {}).get("meters", 2.0)
    # TODO: AI can generate precise motion sequence, velocity limits, and error recovery
    ok = robot.walk_forward(meters)
    return {"success": ok, "meters": meters}


def run_turn(robot: RobotManager, spec: dict) -> dict:
    """Execute turn N degrees. Uses robot_manager.turn()."""
    degrees = spec.get("params", {}).get("degrees", 90)
    # TODO: AI can generate SDK turn command and heading correction
    ok = robot.turn(degrees)
    return {"success": ok, "degrees": degrees}


def run_scan_qr(robot: RobotManager, spec: dict) -> dict:
    """
    Placeholder: Scan QR code / inventory item.
    TODO: AI can generate camera capture, decode QR, and inventory lookup.
    """
    _ = spec
    # TODO: robot.get_sensor_data("camera") -> decode QR -> return item_id / count
    time.sleep(0.2)  # Simulate scan time in sim
    return {"success": True, "scanned": "placeholder", "data": None}


def run_report_dashboard(robot: RobotManager, spec: dict) -> dict:
    """
    Placeholder: Report completion to central dashboard.
    TODO: AI can generate HTTP/WebSocket push to dashboard/dashboard.py.
    """
    _ = spec
    # TODO: POST to dashboard API or append to shared state for dashboard to read
    return {"success": True, "reported": True}


# Map task type -> runner function for pilot loop
_TASK_RUNNERS = {
    TASK_WALK_FORWARD: run_walk_forward,
    TASK_TURN: run_turn,
    TASK_SCAN_QR: run_scan_qr,
    TASK_REPORT_DASHBOARD: run_report_dashboard,
}


def run_single_task(
    controller: FleetController,
    robot_id: str,
    task_id: str,
    task_spec: dict,
) -> dict:
    """
    Execute one task on the given robot: get robot from controller,
    run the task via SDK wrapper, log start/end, report completion.
    """
    robot = controller.get_robot(robot_id)
    if not robot:
        return {"success": False, "error": f"Robot {robot_id} not found"}

    task_type = task_spec.get("type", "")
    runner = _TASK_RUNNERS.get(task_type)
    if not runner:
        return {"success": False, "error": f"Unknown task type: {task_type}"}

    log_utils.log_task_start(task_id, robot_id, task_spec)
    log_utils.log_robot_status(robot_id, {"status": "busy", "task_id": task_id})

    start = time.perf_counter()
    try:
        result = runner(robot, task_spec)
    except Exception as e:  # TODO: AI can add structured error recovery and retries
        result = {"success": False, "error": str(e)}
    duration = time.perf_counter() - start

    log_utils.log_task_end(task_id, robot_id, result, duration)
    controller.report_task_done(robot_id, task_id, result)
    log_utils.log_robot_status(robot_id, {"status": "idle", "last_task": task_id})

    return result


# -----------------------------------------------------------------------------
# Multi-robot coordination: alternate task assignment, status tracking
# -----------------------------------------------------------------------------


def run_pilot(
    num_robots: int = 2,
    sim: bool = True,
    task_specs: list[dict] | None = None,
    host_template: str = "192.168.1.{}",  # e.g. 192.168.1.101, 192.168.1.102
    *,
    domain_id: int = 0,
    interface: str = "",
) -> dict:
    """
    Initialize 1–2 robots via SDK wrapper, assign tasks alternately to each robot,
    track status (idle, busy, completed), and log everything to data/logs/.

    - sim=True: stub only (no SDK, no hardware).
    - sim=False: use SDK. Pass domain_id and interface:
      - MuJoCo: domain_id=1, interface="lo" (start unitree_mujoco first).
      - Real robot: domain_id=0, interface="enp2s0" (or your NIC).
    With SDK, one DDS channel per process; use num_robots=1 for one physical/sim robot.

    Returns summary dict: success, robot_results, fleet_status_final, errors.
    """
    task_specs = task_specs or DEFAULT_TASK_SPECS
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

    # Assign tasks alternately (round-robin) and execute
    results_by_robot: dict[str, list[dict]] = {rid: [] for rid in robot_ids}
    errors: list[str] = []

    for idx, spec in enumerate(task_specs):
        robot_id = robot_ids[idx % num_robots]
        task_id = f"task_{idx}_{spec.get('type', 'unknown')}"

        controller.assign_task(task_id, robot_id, spec)
        result = run_single_task(controller, robot_id, task_id, spec)
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
    }


# -----------------------------------------------------------------------------
# Simulation hooks: entry points for sim vs live
# -----------------------------------------------------------------------------


def is_simulation() -> bool:
    """Return True if running in simulation (e.g. from sim_test or --sim)."""
    return "--sim" in sys.argv or "SIMULATION=1" in str(os.environ.get("SIMULATION", ""))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run R1 fleet pilot (1–2 robots)")
    parser.add_argument("--sim", action="store_true", help="Stub simulation (no SDK, no hardware)")
    parser.add_argument("--mujoco", action="store_true", help="Use SDK with MuJoCo sim (domain_id=1, interface=lo); start unitree_mujoco first")
    parser.add_argument("--interface", type=str, default="", help="Network interface for real robot (e.g. enp2s0); implies SDK, domain_id=0")
    parser.add_argument("--robots", type=int, default=2, choices=(1, 2), help="Number of robots (use 1 with --mujoco or --interface)")
    parser.add_argument("--tasks", type=str, default="", help="Optional: comma-separated task types (future)")
    args = parser.parse_args()

    sim = args.sim
    domain_id = 0
    interface = args.interface or ""
    if args.sim:
        pass  # stub only
    elif args.mujoco:
        sim = False
        domain_id = 1
        interface = "lo"
        if not sdk_available():
            print("unitree_sdk2_python not installed. See SDK/README.md.")
            return 1
    elif args.interface:
        sim = False
        if not sdk_available():
            print("unitree_sdk2_python not installed. See SDK/README.md.")
            return 1
    elif sdk_available():
        # No flags: use SDK and default to MuJoCo (domain 1, lo) for full E2E when SDK is installed
        sim = False
        domain_id = 1
        interface = "lo"
    else:
        if args.mujoco or args.interface:
            print("unitree_sdk2_python not installed. Install from SDK/unitree_sdk2_python (see SDK/README.md).")
        else:
            print("No SDK installed. Use --sim for stub, or install unitree_sdk2_python (see SDK/README.md).")
        return 1

    # Optional: override task list from --tasks (skeleton for AI extension)
    task_specs = None
    if args.tasks:
        # TODO: Parse args.tasks into task_specs list
        pass

    summary = run_pilot(
        num_robots=args.robots,
        sim=sim,
        task_specs=task_specs,
        domain_id=domain_id,
        interface=interface,
    )
    print("Pilot finished. Success:", summary["success"])
    if summary.get("error"):
        print("Error:", summary["error"])
    if "fleet_status_final" in summary:
        print("Fleet status (robots):", [r.get("robot_id") for r in summary["fleet_status_final"]["robots"]])
    if summary.get("errors"):
        print("Errors:", summary["errors"])
    print("Logs written to:", log_utils.get_log_dir())

    return 0 if summary["success"] else 1


if __name__ == "__main__":
    exit(main())
