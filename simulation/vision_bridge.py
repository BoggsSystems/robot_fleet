import argparse
import os
import sys
import numpy as np
import time
import zmq
import cv2
import threading

# Allow importing from the SDK's simulate_python directory
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SDK_SIM_PATH = os.path.join(REPO_ROOT, 'SDK/unitree_mujoco/simulate_python')
sys.path.insert(0, SDK_SIM_PATH)

import mujoco
import config
config.ROBOT = "g1"

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_

class VisionBridge:
    def __init__(self, scene_path, domain_id, interface):
        print(f"[Vision] Loading scene: {scene_path}")
        self.mj_model = mujoco.MjModel.from_xml_path(scene_path)
        self.mj_data = mujoco.MjData(self.mj_model)
        
        self.domain_id = domain_id
        self.interface = interface
        
        # ZeroMQ setup
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        port = 5555 + (domain_id % 100)
        self.socket.bind(f"tcp://*:{port}")
        
        # Renderer setup (640x480)
        self.renderer = mujoco.Renderer(self.mj_model, 480, 640)
        # G1 usually has head_camera. If not found, use first camera.
        try:
            self.camera_id = self.mj_model.camera("head_camera").id
        except ValueError:
            self.camera_id = 0
            print("[Vision] 'head_camera' not found, using default camera 0")
        
        self.running = True
        self.last_sync_time = 0
        self._state_lock = threading.Lock()

        print(f"[Vision] Bridge ready on domain {domain_id}. Streaming on port {port}")

    def on_low_state(self, msg: LowState_):
        """Callback to sync joint positions from the main physics bridge."""
        with self._state_lock:
            # Sync root pose (G1 has a freejoint at the beginning of mj_model.qpos)
            # LowState contains the robot's state (IMU, motors)
            # In simulation, the bridge publishes the full MjData state if configured,
            # but usually it's motor data.
            # For a perfect sync, we'd need a custom 'SimulationState' message,
            # but we can approximate or use a dedicated bridge.
            
            # For now, let's sync the motor positions (qpos[7:])
            # G1 motors start at index 7 (after 7 bytes of root pose)
            for i, motor in enumerate(msg.motor_state):
                if i + 7 < len(self.mj_data.qpos):
                    self.mj_data.qpos[i + 7] = motor.q
            
            # We also need the root pose (body position/quat)
            # Typically this is in msg.imu_state or position telemetry
            # Since this is a specialized "sim-vision" bridge, we'll assume
            # the robot is roughly at the origin or we'll add a Pose message later.
            self.last_sync_time = time.time()

    def run(self):
        # Initialize DDS
        ChannelFactoryInitialize(self.domain_id, self.interface)
        sub = ChannelSubscriber("rt/lowstate", LowState_)
        sub.Init(self.on_low_state, 10)
        
        try:
            while self.running:
                start_time = time.perf_counter()
                
                with self._state_lock:
                    # Basic physics step to resolve any constraints
                    mujoco.mj_forward(self.mj_model, self.mj_data)
                    self.renderer.update_scene(self.mj_data, camera=self.camera_id)
                    frame = self.renderer.render()
                
                if frame is not None:
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    _, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    self.socket.send(buffer.tobytes())
                
                # ~20 FPS
                elapsed = time.perf_counter() - start_time
                time.sleep(max(0, 0.05 - elapsed))
        except KeyboardInterrupt:
            pass
        finally:
            self.socket.close()
            self.context.term()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", required=True)
    parser.add_argument("--domain", type=int, required=True)
    parser.add_argument("--interface", default="lo0")
    args = parser.parse_args()
    
    bridge = VisionBridge(args.scene, args.domain, args.interface)
    bridge.run()
