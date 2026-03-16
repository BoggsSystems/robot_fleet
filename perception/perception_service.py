import zmq
import cv2
import numpy as np
import time
import json
from unitree_sdk2py.core.channel import ChannelPublisher
from ultralytics import YOLO

class PerceptionService:
    def __init__(self, domain_id=100):
        self.domain_id = domain_id
        
        # ZMQ subscriber (from simulator)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        port = 5555 + (domain_id % 100)
        self.socket.connect(f"tcp://localhost:{port}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        
        # ZMQ publisher (results)
        self.result_socket = self.context.socket(zmq.PUB)
        result_port = 5555 + (domain_id % 100) + 10 # 5565, 5566, etc.
        self.result_socket.bind(f"tcp://*:{result_port}")
        
        # YOLO model setup (nano version for speed)
        self.model = YOLO("yolov8n.pt")
        
        self.running = True
        print(f"[Perception Service] Watching Robot {domain_id} on port {port}")

    def run(self):
        while self.running:
            try:
                # Receive frame
                image_data = self.socket.recv(flags=zmq.NOBLOCK)
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # AI Processing via YOLOv8
                    results = self.model(frame, verbose=False, stream=False)
                    
                    # Get annotated frame for visualization
                    annotated_frame = results[0].plot()
                    
                    # Log activity
                    cls_ids = results[0].boxes.cls.tolist()
                    names = results[0].names
                    detections = []
                    for cls_id in cls_ids:
                        name = names[int(cls_id)]
                        detections.append(name)
                    
                    if len(detections) > 0:
                        print(f"[Perception] Detected: {detections}")
                        # Broadcast detections as JSON
                        self.result_socket.send_string(json.dumps(detections))
                    
                    # Show local debug view
                    cv2.imshow(f"AI Vision - Robot {self.domain_id}", annotated_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                        
            except zmq.Again:
                time.sleep(0.01)
                continue
            except KeyboardInterrupt:
                break

    def stop(self):
        self.running = False
        self.socket.close()
        self.context.term()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    domain = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    service = PerceptionService(domain)
    service.run()
