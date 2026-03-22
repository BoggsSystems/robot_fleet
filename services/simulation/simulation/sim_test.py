"""
Simulation script for multi-robot coordination.

Runs fleet_control and tasks in a virtual environment without real hardware.
Use for testing task assignment, conflict resolution, and task logic.
"""

import time
import threading
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fleet_control.controller import FleetController
from fleet_control.robot_manager import RobotManager
from tasks import inventory_scan


def create_sim_robots(controller: FleetController, configs: list[dict]) -> list[RobotManager]:
    """Create RobotManager instances mapped to specific MuJoCo DDS domains."""
    robots = []
    for cfg in configs:
        rm = RobotManager(
            robot_id=cfg["name"],
            domain_id=cfg["domain_id"],
            interface=cfg["interface"],
            sim=False  # We want it to use the real SDK to talk to our MuJoCo bridge
        )
        print(f"Connecting {cfg['name']} to MuJoCo on domain {cfg['domain_id']}...")
        if rm.connect():
            print(f"[{cfg['name']}] Standing up...")
            rm.stand_up()
            controller.register_robot(cfg["name"], robot_manager=rm)
            robots.append(rm)
        else:
            print(f"Failed to connect {cfg['name']}.")
    return robots


def run_multi_robot_sim() -> dict:
    """
    Run a multi-robot simulation with the given warehouse tasks.
    """
    controller = FleetController()
    
    # Start the FastAPI Dashboard Server in a background thread so it can stream data
    from dashboard import server
    dashboard_thread = threading.Thread(
        target=server.run_server, 
        args=(controller, 8000), 
        daemon=True
    )
    dashboard_thread.start()
    
    # We match the domains from our multi_g1_sim.py script
    robot_configs = [
        {"name": "g1_0", "domain_id": 100, "interface": "lo0"},
        {"name": "g1_1", "domain_id": 101, "interface": "lo0"},
    ]
    
    robots = create_sim_robots(controller, robot_configs)
    if len(robots) < 2:
        print("Waiting for MuJoCo simulation to be fully started. Make sure you run simulation/multi_g1_sim.py first!")
        return {"success": False}

    print("Both robots connected! Assigning tasks...")
    
    # Shelf 1 task for Robot 0
    task1 = {
        "task_id": "audit_shelf_1",
        "robot_id": robots[0].robot_id,
        "zones": [
            {"zone_id": "shelf_1_front", "x": -2.0, "y": -2.0},
            {"zone_id": "shelf_1_mid", "x": -2.0, "y": 0.0},
            {"zone_id": "shelf_1_back", "x": -2.0, "y": 2.0},
        ]
    }
    
    # Shelf 2 task for Robot 1
    task2 = {
        "task_id": "audit_shelf_2",
        "robot_id": robots[1].robot_id,
        "zones": [
            {"zone_id": "shelf_2_front", "x": 2.0, "y": -2.0},
            {"zone_id": "shelf_2_mid", "x": 2.0, "y": 0.0},
            {"zone_id": "shelf_2_back", "x": 2.0, "y": 2.0},
        ]
    }
    
    controller.assign_task(task1["task_id"], task1["robot_id"], task1)
    controller.assign_task(task2["task_id"], task2["robot_id"], task2)
    
    def run_worker(robot, task):
        print(f"[{robot.robot_id}] Starting task: {task['task_id']}")
        res = inventory_scan.run_inventory_scan(
            robot, 
            task["zones"], 
            robot_id=robot.robot_id
        )
        controller.report_task_done(robot.robot_id, task["task_id"], res)
        print(f"[{robot.robot_id}] Finished task. Success: {res['success']}")
        
    t1 = threading.Thread(target=run_worker, args=(robots[0], task1))
    t2 = threading.Thread(target=run_worker, args=(robots[1], task2))
    
    start = time.time()
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    duration = time.time() - start
    print(f"\nAll tasks completed in {duration:.2f} seconds.")
    print(f"Final Fleet Status:\n{controller.get_fleet_status()}")
    
    # Disconnect
    for r in robots:
        r.disconnect()

    return {"success": True, "duration_sec": duration}


if __name__ == "__main__":
    run_multi_robot_sim()
