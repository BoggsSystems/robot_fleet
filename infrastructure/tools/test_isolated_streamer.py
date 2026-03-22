import mujoco
import cv2
import zmq
import numpy as np
import time
import os

# Path to the scene
SCENE = "/Users/jeffboggs/robot_fleet/SDK/unitree_mujoco/unitree_robots/g1/box_training_scene.xml"

def test_streamer():
    print(f"Loading model: {SCENE}")
    model = mujoco.MjModel.from_xml_path(SCENE)
    data = mujoco.MjData(model)
    
    # Setup ZMQ
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:5555")
    
    # Setup Renderer
    print("Initializing Renderer...")
    renderer = mujoco.Renderer(model, 480, 640)
    cam_id = model.camera("head_camera").id
    
    print("Starting rendering loop (10 frames)...")
    for i in range(10):
        mujoco.mj_step(model, data)
        renderer.update_scene(data, camera=cam_id)
        frame = renderer.render()
        
        if frame is not None:
            print(f"Frame {i} rendered: {frame.shape}")
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            _, buffer = cv2.imencode('.jpg', frame_bgr)
            socket.send(buffer.tobytes())
        else:
            print(f"Frame {i} is NULL")
        
        time.sleep(0.1)
    
    print("Done. Check if receiver saw 10 frames.")
    socket.close()
    context.term()

if __name__ == "__main__":
    test_streamer()
