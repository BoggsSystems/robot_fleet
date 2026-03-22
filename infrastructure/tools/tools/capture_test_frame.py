import zmq
import cv2
import numpy as np
import sys
import os

def capture_frame(port=5555):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://localhost:{port}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    socket.setsockopt(zmq.RCVTIMEO, 5000) # 5s timeout

    print(f"Polling for frame on port {port}...")
    try:
        image_data = socket.recv()
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is not None:
            output_path = "/Users/jeffboggs/robot_fleet/tools/debug_frame.png"
            cv2.imwrite(output_path, frame)
            print(f"Captured frame saved to {output_path}")
            return True
        else:
            print("Failed to decode frame.")
            return False
    except zmq.Again:
        print("Timeout waiting for frame. Is the streamer running?")
        return False
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    capture_frame()
