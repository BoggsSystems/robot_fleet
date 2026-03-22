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
config.SIMULATE_DT = 0.0005 # 2000Hz for rock-solid stability
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
# Scale down KP for simulation stability with suspenders
KP = [40, 40, 40, 80, 20, 20,   40, 40, 40, 80, 20, 20,  30, 30, 30,  20, 20, 20, 20, 20, 20, 20,  20, 20, 20, 20, 20, 20, 20]
KD = [5, 5, 5, 10, 5, 5,        5, 5, 5, 10, 5, 5,       5, 5, 5,     2, 2, 2, 2, 2, 2, 2,     2, 2, 2, 2, 2, 2, 2]

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
        
        self.vx = 0.0
        self.vyaw = 0.0
        
        self.sweep_mode = False
        self.sweep_start_time = 0.0
        
        # Sanitation Mission
        self.sanitation_mode = False
        self.sanitation_state = "SCAN"
        self.target_item_id = -1
        self.bin_pos = np.array([0.5, 0.5, 1.15])
        self.last_scan_time = 0.0
        
    def enable_sweep(self):
        print("[Teleop] Sweep Mode ENABLED")
        self.sweep_mode = True
        self.sweep_start_time = time.time()
        self.enabled = True
        self.standing = True # Start by standing
        self.vx = 0.0 

    def enable_sanitation(self):
        print("[Teleop] Sanitation Mode ENABLED (WAITING in Hallway)")
        self.sanitation_mode = True
        self.sanitation_state = "WAITING"
        self.enabled = True
        self.standing = True
        
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
        elif key == 71: # 'G' for Garbage Mission Start
            if self.sanitation_mode and self.sanitation_state == "WAITING":
                print("[Sanitation] MISSION TRIGGERED - Entering Bathroom...")
                self.sanitation_state = "ENTERING"

    def step(self, mj_model=None, mj_data=None):
        self.time += self.dt
        
        if not self.enabled:
            return

        # Autonomous Sequence for Sanitation Mode (Sanitation State Machine)
        if self.sanitation_mode and mj_data is not None:
            if self.sanitation_state == "WAITING":
                # Just stand still in hallway
                self.vx = 0.0
                self.vyaw = 0.0
                self.standing = True
                
            elif self.sanitation_state == "ENTERING":
                # Gantry handle movement to entrance
                self.standing = False
                self.vx = 0.4 # Active walking
                
            elif self.sanitation_state == "SCAN":
                # Find nearest trash item (2Hz frequency to save CPU)
                self.standing = True
                self.vx = 0.0
                
                if mj_data.time - self.last_scan_time < 0.5:
                    return
                self.last_scan_time = mj_data.time
                
                min_dist = 100.0
                target_id = -1
                
                # Check for torso bodies safely
                torso_id = -1
                for b_name in ["torso", "torso_link", "pelvis"]:
                    try:
                        torso_id = mj_model.body(b_name).id
                        break
                    except (ValueError, KeyError, AttributeError):
                        continue
                
                if torso_id == -1:
                    print("[Sanitation Error] Could not find robot torso for scanning.")
                    return
                    
                torso_pos = mj_data.xpos[torso_id]
                
                for i in range(mj_model.nbody):
                    name = mujoco.mj_id2name(mj_model, mujoco.mjtObj.mjOBJ_BODY, i)
                    if name and name.startswith("trash_"):
                        # Calculate distance
                        item_pos = mj_data.xpos[i]
                        dist = np.linalg.norm(item_pos[:2] - torso_pos[:2])
                        if dist < min_dist:
                            min_dist = dist
                            target_id = i
                
                if target_id != -1:
                    t_name = mujoco.mj_id2name(mj_model, mujoco.mjtObj.mjOBJ_BODY, target_id)
                    print(f"[Sanitation] Target identified: {t_name}")
                    self.target_item_id = target_id
                    self.sanitation_state = "NAVIGATING"
                else:
                    # Keep scanning
                    pass
                
            elif self.sanitation_state == "NAVIGATING":
                # Gantry handles moving band.point
                self.standing = True
                self.vx = 0.0
                
            elif self.sanitation_state == "PICKING":
                # Simplified: hold position
                self.standing = True
                self.vx = 0.0
                pass

        # Autonomous Sequence for Sweep Mode
        if self.sweep_mode:
            sweep_elapsed = time.time() - self.sweep_start_time
            if sweep_elapsed < 3.0:
                # 0-3s: Stand up and stabilize
                self.standing = True
                self.vx = 0.0
            elif sweep_elapsed < 50.0:
                # 3-50s: Slide mode (no walk gait, just gantry movement)
                self.standing = True 
                self.vx = 0.0        
            else:
                # 50s+: Finish
                print("[Teleop] Sweep Complete. Stopping.")
                self.vx = 0.0
                self.standing = True
                self.sweep_mode = False

        # Autonomous Sequence for Sanitation Mode
        if self.sanitation_mode and self.enabled:
            # We will use mj_data from run_bridge eventually, for now we need a way 
            # to pass mj_data to teleop or have teleop access it.
            # For simplicity, we'll implement the logic in run_bridge and just 
            # use teleop to store the state.
            pass

        # Always populate motor commands if enabled
        startup_multiplier = np.clip((self.time - 0.5) / 2.0, 0.0, 1.0)
        
        phase = self.time * 2.0 * np.pi * 1.5 # 1.5Hz
        
        for i in range(29):
            self.low_cmd.motor_cmd[i].mode = 1
            self.low_cmd.motor_cmd[i].kp = KP[i]
            self.low_cmd.motor_cmd[i].kd = KD[i]
            self.low_cmd.motor_cmd[i].tau = 0.0
            self.low_cmd.motor_cmd[i].dq = 0.0
            
            target_q = 0.0
            
            # Default to stable "crouch" position (bent knees)
            if i in [G1JointIndex.LeftKnee, G1JointIndex.RightKnee]:
                target_q = 0.6 * startup_multiplier
                if not self.standing:
                    # Leg oscillation
                    offset = 0.3 * np.sin(phase if i == G1JointIndex.LeftKnee else phase + np.pi)
                    target_q += offset
            elif i in [G1JointIndex.LeftHipPitch, G1JointIndex.RightHipPitch]:
                target_q = -0.3 * startup_multiplier
                if not self.standing:
                    offset = 0.2 * np.sin(phase if i == G1JointIndex.LeftHipPitch else phase + np.pi)
                    target_q += offset
            elif i == G1JointIndex.WaistPitch:
                target_q = 0.0 # Perfectly upright waist
            elif i in [G1JointIndex.LeftShoulderPitch, G1JointIndex.RightShoulderPitch]:
                target_q = 0.5 * startup_multiplier # Tuck arms a bit
            
            # If walking (vx != 0) and not in 'standing' mode, add wobble
            if not self.standing and self.vx != 0:
                # Stable "shuffle" gait: small oscillations around the crouch point
                phase_offset = 0.0 if i in [G1JointIndex.LeftKnee, G1JointIndex.LeftHipPitch] else np.pi
                if i in [G1JointIndex.LeftKnee, G1JointIndex.RightKnee]:
                    target_q += (0.15 * np.sin(phase + phase_offset)) * startup_multiplier
                if i in [G1JointIndex.LeftHipPitch, G1JointIndex.RightHipPitch]:
                    target_q += (-0.1 * self.vx * np.sin(phase + phase_offset)) * startup_multiplier

            self.low_cmd.motor_cmd[i].q = target_q

        self.low_cmd.crc = self.crc.Crc(self.low_cmd)
        self.publisher.Write(self.low_cmd)

# OpenGL context conflicts on macOS.

class Suspenders(ElasticBand):
    def __init__(self):
        super().__init__()
        self.stiffness = 50.0   # Relaxed hold for more natural walking
        self.z_stiffness = 400.0 
        self.damping = 100.0     
        self.enable = True
        self.point = np.array([0, 0, 1.15]) # Lift higher to clear floor

    def Advance(self, mj_model, mj_data, body_id):
        if not self.enable:
            return np.zeros(6)
            
        x = mj_data.xpos[body_id]
        cvel = mj_data.cvel[body_id]
        dq = cvel[0:3] # angular velocity
        dx = cvel[3:6] # linear velocity
        
        δx = self.point - x
        f = np.zeros(6)
        
        # 1. Translational Force
        f[0:2] = (self.stiffness * δx[0:2] - self.damping * dx[0:2])
        f[2] = (self.z_stiffness * δx[2] - (self.damping * 2.0) * dx[2])
        
        # 2. Leveling Torque (Restores Upright posture)
        # We extract Local Z from the body's rotation matrix (3rd column)
        Rz = mj_data.xmat[body_id, [2, 5, 8]]
        WorldUp = np.array([0, 0, 1])
        
        # Calculate corrective torque direction and magnitude
        torque_error = np.cross(Rz, WorldUp)
        
        # Apply restoration torque and high angular damping
        f[3:6] = 800.0 * torque_error - 120.0 * dq
            
        # NaN Guard
        if np.any(np.isnan(f)):
            return np.zeros(6)
        return f


def run_bridge(scene_path: str, domain_id: int, interface: str, sweep=False, sanitation=False):
    print(f"[Bridge] Loading scene: {scene_path}")
    mj_model = mujoco.MjModel.from_xml_path(scene_path)
    mj_data = mujoco.MjData(mj_model)
    mj_model.opt.timestep = config.SIMULATE_DT

    print(f"[Bridge] Initializing DDS channel: domain={domain_id}, interface={interface}")
    ChannelFactoryInitialize(domain_id, interface)
    
    teleop = TeleopController(domain_id)
    if sweep:
        teleop.enable_sweep()
    if sanitation:
        teleop.enable_sanitation()
    
    # Initialize position for Sanitation mission
    if sanitation:
        print("[Bridge] Setting hallway starting pose...")
        # G1 Pelvis Freejoint qpos (7 elements)
        base_id = mj_model.joint("floating_base_joint").id
        q_idx = mj_model.jnt_qposadr[base_id]
        
        # Position: X=1.93, Y=1.48, Z=0.81 (Above trash_2 inside bathroom)
        mj_data.qpos[q_idx : q_idx+3] = np.array([1.93, 1.48, 0.81])
        # Orientation: Facing East (X+)
        mj_data.qpos[q_idx+3 : q_idx+7] = np.array([1, 0, 0, 0])
        
        # Stable Posture: Bent knees (idx 3 and 9 for leg motors)
        # Note: We use the joint ids found in the XML previously
        mj_data.qpos[mj_model.joint("left_knee_joint").id + 6] = 0.6
        mj_data.qpos[mj_model.joint("right_knee_joint").id + 6] = 0.6
        mj_data.qpos[mj_model.joint("left_hip_pitch_joint").id + 6] = -0.3
        mj_data.qpos[mj_model.joint("right_hip_pitch_joint").id + 6] = -0.3
        
        mujoco.mj_forward(mj_model, mj_data)
    
    band = Suspenders()
    if sanitation:
        band.point = np.array([-1.5, 4.5, 1.15]) # Start closer to door
    else:
        band.point = np.array([0, 0, 1.1]) 
    
    def key_callback(key):
        with locker:
            teleop.on_key(key)

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
                    # Constant Velocity Anchor for Sweep
                    if teleop.sweep_mode:
                        elapsed = time.time() - teleop.sweep_start_time
                        if elapsed > 3.0:
                            # Move anchor forward at fixed 0.1m/s (slower is safer)
                            band.point[0] = (elapsed - 3.0) * 0.1
                        else:
                            band.point[0] = 0.0
                        
                        if mj_data.time % 1.0 < config.SIMULATE_DT:
                            pos_x = mj_data.xpos[torso_id][0]
                            print(f"[Sweep] Robot X: {pos_x:.2f}m")
                        
                        if mj_data.time % 1.0 < config.SIMULATE_DT:
                            print(f"[Sweep] Robot X: {mj_data.xpos[torso_id][0]:.2f}m")
                        
                        band.point[1] = 0.0
                        band.point[2] = 1.15             # Match 1.15m anchor height
                        
                    elif teleop.sanitation_mode:
                        # Dynamic Gantry Control for Sanitation
                        if teleop.sanitation_state == "WAITING":
                            # Hold hallway position
                            band.point[:2] = np.array([-1.5, 4.5])
                            band.point[2] = 1.15
                            
                        elif teleop.sanitation_state == "ENTERING":
                            # Navigate towards bathroom center (1.5, 4.5)
                            entrance_target = np.array([1.5, 4.5, 1.15])
                            diff = entrance_target - band.point
                            dist = np.linalg.norm(diff[:2])
                            if dist > 0.05:
                                dir_xy = diff[:2] / dist
                                band.point[:2] += dir_xy * 0.005 # Snappier glide
                            else:
                                print("[Sanitation] Entered bathroom. Starting scan.")
                                teleop.sanitation_state = "SCAN"
                                
                        elif teleop.sanitation_state == "NAVIGATING":
                            # Target is the trash item
                            tg_pos = mj_data.xpos[teleop.target_item_id]
                            # Move anchor point towards target (low pass/limited speed)
                            diff = tg_pos - band.point
                            dist = np.linalg.norm(diff[:2])
                            
                            if dist > 0.1:
                                # Slide towards trash
                                dir_xy = diff[:2] / dist
                                band.point[:2] += dir_xy * 0.0001 # Slow slide
                            else:
                                # Arrived
                                print(f"[Sanitation] Arrived at item. Switching to PICKING.")
                                teleop.sanitation_state = "PICKING"
                        
                        elif teleop.sanitation_state == "PICKING":
                            # Lower gantry to grasp
                            band.point[2] = 0.9 # Closer to floor
                            # Simulate time to pick
                            if mj_data.time % 5.0 < config.SIMULATE_DT:
                                print(f"[Sanitation] Item collected. Returning to scan.")
                                # Hide the 'collected' object (move it deep underground)
                                q_addr = mj_model.jnt_qposadr[mj_model.body(teleop.target_item_id).jntadr[0]]
                                mj_data.qpos[q_addr:q_addr+3] = np.array([0, 0, -5.0])
                                teleop.sanitation_state = "SCAN"
                                band.point[2] = 1.15
                            
                        elif teleop.sanitation_state == "DEPOSITING":
                            # Move anchor towards bin_pos
                            diff = teleop.bin_pos - band.point
                            dist = np.linalg.norm(diff[:2])
                            if dist > 0.1:
                                dir_xy = diff[:2] / dist
                                band.point[:2] += dir_xy * 0.0001
                            else:
                                print(f"[Sanitation] Arrived at bin. Depositing.")
                                teleop.sanitation_state = "SCAN"
                                band.point[2] = 1.15

                    # Apply combined force and torque to torso
                    f_tau = band.Advance(mj_model, mj_data, torso_id)
                    mj_data.xfrc_applied[torso_id, :] = f_tau

                # Run teleop at ~100Hz (every 2 steps if dt=0.005)
                if cnt % 2 == 0:
                    teleop.step(mj_model, mj_data)
                if cnt % 1000 == 0:
                    base_pos = mj_data.xpos[torso_id]
                    print(f"[Bridge] Robot at X={base_pos[0]:.2f}, Y={base_pos[1]:.2f}, Z={base_pos[2]:.2f} (State: {teleop.sanitation_state})")

            # Physics step OUTSIDE the lock to keep GUI responsive
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
    parser.add_argument("--sweep", action="store_true", help="Start in autonomous sweep mode")
    parser.add_argument("--sanitation", action="store_true", help="Start in autonomous sanitation (garbage collection) mode")
    args = parser.parse_args()

    # Resolve relative to current working directory (not the script dir)
    scene_path = args.scene if os.path.isabs(args.scene) else os.path.abspath(args.scene)
    
    # Pass flags to run_bridge
    run_bridge(scene_path, args.domain, args.interface, sweep=args.sweep, sanitation=args.sanitation)
