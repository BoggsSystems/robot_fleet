import zmq
import cv2
import numpy as np
import sys

def main():
    domain_id = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    port = 5555 + (domain_id % 100)
    
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://localhost:{port}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    
    print(f"Connected to robot stream on port {port}. Press 'q' to quit.")
    
    while True:
        try:
            image_data = socket.recv(flags=zmq.NOBLOCK)
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                cv2.imshow(f"Robot {domain_id} View", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except zmq.Again:
            continue
        except KeyboardInterrupt:
            break

    cv2.destroyAllWindows()
    socket.close()
    context.term()

if __name__ == "__main__":
    main()
