"""
Multi-Robot MuJoCo Launcher for Unitree G1.

Spawns one bridge subprocess per robot, each with its own:
  - MuJoCo physics + viewer window
  - DDS domain (100 for g1_0, 101 for g1_1)
  - Full UnitreeSdk2Bridge command/state loop

This is the "full fix" architecture. Since ChannelFactoryInitialize is a
process-level singleton, each robot must run in its own OS process.

Usage:
    python3 multi_g1_sim.py

Then in a separate terminal, run:
    python3 sim_test.py
"""

import subprocess
import sys
import os
import time
import signal

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
VENV_PYTHON = os.path.join(REPO_ROOT, "venv", "bin", "python3")
RUNNER = os.path.join(HERE, "run_robot_bridge.py")

# macOS requires mujoco.viewer.launch_passive to be run under mjpython
MJPYTHON = os.path.join(REPO_ROOT, "venv", "bin", "mjpython")
# Fall back to regular python if mjpython not found (Linux/Windows)
PYTHON = MJPYTHON if os.path.exists(MJPYTHON) else (VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable)

G1_DIR = os.path.join(REPO_ROOT, "SDK/unitree_mujoco/unitree_robots/g1")

ROBOT_CONFIGS = [
    {
        "name": "g1_0",
        "scene": os.path.join(G1_DIR, "warehouse_g1_0.xml"),
        "domain": 100,
        "interface": "lo0",
    },
    {
        "name": "g1_1",
        "scene": os.path.join(G1_DIR, "warehouse_g1_1.xml"),
        "domain": 101,
        "interface": "lo0",
    },
]


def launch_robot(cfg: dict) -> subprocess.Popen:
    """Spawn a bridge runner subprocess for a single robot."""
    cmd = [
        PYTHON, RUNNER,
        "--scene", cfg["scene"],
        "--domain", str(cfg["domain"]),
        "--interface", cfg["interface"],
    ]
    env = os.environ.copy()
    env["CYCLONEDDS_HOME"] = os.path.expanduser("~/cyclonedds/install")
    print(f"[Launcher] Starting {cfg['name']} on domain {cfg['domain']}...")
    proc = subprocess.Popen(cmd, env=env)
    return proc


def main():
    processes = []
    for cfg in ROBOT_CONFIGS:
        proc = launch_robot(cfg)
        processes.append((cfg["name"], proc))
        # Brief stagger so the two MuJoCo windows don't fight for DDS init
        time.sleep(1.5)

    print(f"\n[Launcher] All {len(processes)} robot bridges started.")
    print("[Launcher] Now run `python3 sim_test.py` in a new terminal to dispatch tasks.")
    print("[Launcher] Press Ctrl+C to shut down all bridges.\n")

    def shutdown(sig, frame):
        print("\n[Launcher] Shutting down all robot bridges...")
        for name, proc in processes:
            proc.terminate()
            print(f"  Terminated {name}")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Wait for all subprocesses — they exit when the MuJoCo viewer is closed
    for name, proc in processes:
        proc.wait()
        print(f"[Launcher] {name} bridge exited.")


if __name__ == "__main__":
    main()
