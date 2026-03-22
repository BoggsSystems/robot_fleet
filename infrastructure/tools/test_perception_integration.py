import time
import os
import sys

# Allow importing from fleet_control
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fleet_control.robot_manager import RobotManager

def test_perception():
    print("Initializing RobotManager for Robot g1_0 (Domain 100)...")
    robot = RobotManager("g1_0", domain_id=100, interface="lo0")
    
    if not robot.connect():
        print("Failed to connect to robot bridge.")
        return

    print("Connected. Listening for detections from AI Perception Service...")
    print("Press Ctrl+C to exit.")
    
    try:
        while True:
            # Check for detections in the latest status
            status = robot.get_status()
            detections = status.get("detections", [])
            
            if detections:
                print(f"[RobotManager] {robot.robot_id} sees: {detections}")
            
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        robot.disconnect()

if __name__ == "__main__":
    test_perception()
