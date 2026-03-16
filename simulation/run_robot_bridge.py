"""
Single-robot MuJoCo bridge runner.

Runs a full UnitreeSdk2Bridge for a single G1 robot in its own process.
This is meant to be launched as a subprocess by multi_g1_sim.py, one
instance per robot, each on a distinct DDS domain_id.

Usage:
    python3 run_robot_bridge.py --scene g1_0_scene.xml --domain 100 --interface lo0
"""

import argparse
import time
import os
import sys
import threading

# Allow importing from the SDK's simulate_python directory
SDK_SIM_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../SDK/unitree_mujoco/simulate_python'))
sys.path.insert(0, SDK_SIM_PATH)

import mujoco
import mujoco.viewer
from threading import Thread

# We must set config's ROBOT before importing the bridge — it reads at module level
import config
config.ROBOT = "g1"
config.SIMULATE_DT = 0.005
config.VIEWER_DT = 0.02
config.USE_JOYSTICK = False
config.PRINT_SCENE_INFORMATION = False
config.ENABLE_ELASTIC_BAND = False

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py_bridge import UnitreeSdk2Bridge
config.VIEWER_DT = 0.02
config.USE_JOYSTICK = False
config.PRINT_SCENE_INFORMATION = False
config.ENABLE_ELASTIC_BAND = False


def run_bridge(scene_path: str, domain_id: int, interface: str):
    print(f"[Bridge] Loading scene: {scene_path}")
    mj_model = mujoco.MjModel.from_xml_path(scene_path)
    mj_data = mujoco.MjData(mj_model)
    mj_model.opt.timestep = config.SIMULATE_DT

    viewer = mujoco.viewer.launch_passive(mj_model, mj_data)
    locker = threading.Lock()

    print(f"[Bridge] Initializing DDS channel: domain={domain_id}, interface={interface}")
    ChannelFactoryInitialize(domain_id, interface)
    unitree = UnitreeSdk2Bridge(mj_model, mj_data)
    print(f"[Bridge] Bridge ready on domain {domain_id}. Entering physics loop.")

    def simulation_thread():
        while viewer.is_running():
            step_start = time.perf_counter()
            with locker:
                mujoco.mj_step(mj_model, mj_data)
            sleep_time = mj_model.opt.timestep - (time.perf_counter() - step_start)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def viewer_thread():
        while viewer.is_running():
            with locker:
                viewer.sync()
            time.sleep(config.VIEWER_DT)

    sim_t = Thread(target=simulation_thread, daemon=True)
    view_t = Thread(target=viewer_thread, daemon=True)

    sim_t.start()
    view_t.start()

    # Block main thread until viewer closes
    sim_t.join()
    view_t.join()
    print(f"[Bridge] Domain {domain_id} exiting.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Single-robot MuJoCo SDK bridge runner")
    parser.add_argument("--scene", required=True, help="Path to the robot's MuJoCo scene XML")
    parser.add_argument("--domain", type=int, required=True, help="DDS domain ID for this robot")
    parser.add_argument("--interface", default="lo0", help="Network interface (default: lo0 for loopback)")
    args = parser.parse_args()

    # Resolve relative to current working directory (not the script dir)
    scene_path = args.scene if os.path.isabs(args.scene) else os.path.abspath(args.scene)
    run_bridge(scene_path, args.domain, args.interface)
