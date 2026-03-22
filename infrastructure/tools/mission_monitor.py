import zmq
import cv2
import numpy as np
import time
import os
import sys

# Monitoring script to ensure the robot is up and walking
def monitor_sweep(duration_mins=5):
    print(f"Monitoring mission for {duration_mins} minutes...")
    output_dir = "/Users/jeffboggs/.gemini/antigravity/brain/e9ca256b-344b-4186-8008-d49da1fb3689"
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup ZMQ subscriber for frames
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5555")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    socket.setsockopt(zmq.RCVTIMEO, 2000)

    start_time = time.time()
    frame_count = 0
    
    try:
        while time.time() - start_time < (duration_mins * 60):
            try:
                image_data = socket.recv()
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Save a log frame every 10 seconds
                    if int(time.time() - start_time) % 10 == 0:
                        path = os.path.join(output_dir, "sweep_log_frame.png")
                        cv2.imwrite(path, frame)
                        print(f"[{time.strftime('%H:%M:%S')}] Frame captured and saved.")
                
                frame_count += 1
            except zmq.Again:
                print(f"[{time.strftime('%H:%M:%S')}] WARNING: No video frame received.")
            
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("Monitoring stopped.")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    monitor_sweep()
