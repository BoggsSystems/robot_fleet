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
import zmq
import cv2

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
config.ENABLE_ELASTIC_BAND = True # Enable virtual tether for stability

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelPublisher
from unitree_sdk2py_bridge import UnitreeSdk2Bridge, ElasticBand
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.utils.crc import CRC
import numpy as np

# G1 Joint Indices for 29DOF model
class G1JointIndex:
    LeftHipPitch = 0
    LeftHipRoll = 1
    LeftHipYaw = 2
    LeftKnee = 3
    LeftAnklePitch = 4
    LeftAnkleRoll = 5
    RightHipPitch = 6
    RightHipRoll = 7
    RightHipYaw = 8
    RightKnee = 9
    RightAnklePitch = 10
    RightAnkleRoll = 11
    WaistYaw = 12
    WaistRoll = 13
    WaistPitch = 14
    LeftShoulderPitch = 15
    LeftShoulderRoll = 16
    LeftShoulderYaw = 17
    LeftElbow = 18
    LeftWristRoll = 19
    LeftWristPitch = 20
    LeftWristYaw = 21
    RightShoulderPitch = 22
    RightShoulderRoll = 23
    RightShoulderYaw = 24
    RightElbow = 25
    RightWristRoll = 26
    RightWristPitch = 27
    RightWristYaw = 28

# Basic stable PD gains for G1
# Leg indices: 0-5 (left), 6-11 (right)
# High damping (KD) is key for simulation stability
KP = [80, 80, 80, 150, 40, 40,  80, 80, 80, 150, 40, 40,  60, 60, 60,  40, 40, 40, 40, 40, 40, 40,  40, 40, 40, 40, 40, 40, 40]
KD = [10, 10, 10, 20, 10, 10,  10, 10, 10, 20, 10, 10,  10, 10, 10,  5, 5, 5, 5, 5, 5, 5,  5, 5, 5, 5, 5, 5, 5]

class TeleopController:
    def __init__(self, domain_id):
        self.domain_id = domain_id
        self.publisher = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.publisher.Init()
        self.crc = CRC()
        self.low_cmd = unitree_hg_msg_dds__LowCmd_()
        
        self.enabled = False
        self.standing = True  # Start standing immediately
        self.time = 0.0
        self.dt = 0.01
        
        # Movement state
        self.vx = 0.3  # Start walking immediately
        self.vyaw = 0.0
        
    def on_key(self, key):
        # MuJoCo/GLFW key codes
        if key == 76: # 'L' for Lift/Stand
            self.standing = not self.standing
            print(f"[Teleop] Standing: {self.standing}")
        elif key == 87: # 'W'
            self.vx = 0.5
        elif key == 83: # 'S'
            self.vx = -0.5
        elif key == 65: # 'A'
            self.vyaw = 0.5
        elif key == 68: # 'D'
            self.vyaw = -0.5
        elif key == 32: # Space to stop
            self.vx = 0.0
            self.vyaw = 0.0
            print("[Teleop] Stop")

    def step(self):
        self.time += self.dt
        
        # Wait 1.0s before starting to allow model to settle
        if self.time < 1.0:
            return

        if not self.standing:
            return

        # Simple procedural "wobble" walk if vx != 0
        # Use a startup multiplier to ramp up movements over 2 seconds
        startup_multiplier = np.clip((self.time - 1.0) / 2.0, 0.0, 1.0)
        
        phase = self.time * 2.0 * np.pi * 1.5 # 1.5Hz
        
        for i in range(29):
            self.low_cmd.motor_cmd[i].mode = 1
            self.low_cmd.motor_cmd[i].kp = KP[i]
            self.low_cmd.motor_cmd[i].kd = KD[i]
            self.low_cmd.motor_cmd[i].tau = 0.0
            self.low_cmd.motor_cmd[i].dq = 0.0
            
            # Default to stable "crouch" position (bent knees)
            # This lowers the CoM and makes the procedural wobble much safer
            if i in [G1JointIndex.LeftKnee, G1JointIndex.RightKnee]:
                target_q = 0.6 * startup_multiplier
            elif i in [G1JointIndex.LeftHipPitch, G1JointIndex.RightHipPitch]:
                target_q = -0.3 * startup_multiplier
            elif i == G1JointIndex.WaistPitch:
                target_q = 0.1 * startup_multiplier # Slight forward lean
            else:
                target_q = 0.0
            
            if self.vx != 0:
                # Stable "shuffle" gait: small oscillations around the crouch point
                phase_offset = 0.0 if i in [G1JointIndex.LeftKnee, G1JointIndex.LeftHipPitch] else np.pi
                if i in [G1JointIndex.LeftKnee, G1JointIndex.RightKnee]:
                    target_q += (0.15 * np.sin(phase + phase_offset)) * startup_multiplier
                if i in [G1JointIndex.LeftHipPitch, G1JointIndex.RightHipPitch]:
                    target_q += (-0.1 * self.vx * np.sin(phase + phase_offset)) * startup_multiplier

            self.low_cmd.motor_cmd[i].q = target_q

        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.publisher.Write(self.low_cmd)

# Note: PerceptionStreamer removed. Use vision_bridge.py in a separate process to avoid 
# OpenGL context conflicts on macOS.


def run_bridge(scene_path: str, domain_id: int, interface: str):
    print(f"[Bridge] Loading scene: {scene_path}")
    mj_model = mujoco.MjModel.from_xml_path(scene_path)
    mj_data = mujoco.MjData(mj_model)
    mj_model.opt.timestep = config.SIMULATE_DT

    print(f"[Bridge] Initializing DDS channel: domain={domain_id}, interface={interface}")
    ChannelFactoryInitialize(domain_id, interface)
    
    teleop = TeleopController(domain_id)
    band = ElasticBand()
    band.point = np.array([0, 0, 1.2]) # Tether height for G1
    
    def key_callback(key):
        teleop.on_key(key)
        band.MujuocoKeyCallback(key)

    viewer = mujoco.viewer.launch_passive(mj_model, mj_data, key_callback=key_callback)
    locker = threading.Lock()

    unitree = UnitreeSdk2Bridge(mj_model, mj_data)
    
    # Identify torso for elastic band
    torso_id = mj_model.body("torso_link").id

    print(f"[Bridge] Bridge ready on domain {domain_id}. Entering physics loop.")
    print("[Teleop] Controls: L=Stand, W/S=Forward/Back, A/D=Turn, Space=Stop")
    print("[Tether] Controls: 9=Toggle, 7/8=Lower/Lift")

    def simulation_thread():
        cnt = 0
        while viewer.is_running():
            step_start = time.perf_counter()
            with locker:
                # Apply Elastic Band (Virtual Tether) force
                if config.ENABLE_ELASTIC_BAND and band.enable:
                    mj_data.xfrc_applied[torso_id, :3] = band.Advance(
                        mj_data.qpos[:3], mj_data.qvel[:3]
                    )

                # Run teleop at ~100Hz (every 2 steps if dt=0.005)
                if cnt % 2 == 0:
                    teleop.step()
                mujoco.mj_step(mj_model, mj_data)
                cnt += 1
            
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
