import subprocess
import time
import os
import signal
import sys

def launch_sanitation():
    print("[Sanitation] Starting Bathroom Sanitation Scenario...")
    
    # Paths
    repo_root = "/Users/jeffboggs/robot_fleet"
    python_exe = os.path.join(repo_root, "venv/bin/python3")
    mjpython_exe = os.path.join(repo_root, "venv/bin/mjpython")
    scene_xml = os.path.join(repo_root, "simulation/bathroom_scene.xml")
    bridge_script = os.path.join(repo_root, "simulation/run_robot_bridge.py")
    vision_script = os.path.join(repo_root, "simulation/vision_bridge.py")
    perception_script = os.path.join(repo_root, "perception/perception_service.py")
    
    # 1. Start the Physics Bridge (Domain 100)
    # We use sanitation mode flag
    bridge_proc = subprocess.Popen([
        mjpython_exe, bridge_script,
        "--scene", scene_xml,
        "--domain", "100",
        "--sanitation"
    ])
    
    time.sleep(2) # Wait for bridge to init
    
    # 2. Start the Vision Bridge
    vision_proc = subprocess.Popen([
        python_exe, vision_script,
        "--scene", scene_xml,
        "--domain", "100"
    ])
    
    # 3. Start the Perception Service (AI Brain)
    perception_proc = subprocess.Popen([
        python_exe, perception_script,
        "100"
    ])
    
    print("\n[Sanitation] Mission Running!")
    print("[Sanitation] The G1 is patrolling the bathroom for trash.")
    print("[Sanitation] Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Sanitation] Stopping mission...")
        bridge_proc.terminate()
        vision_proc.terminate()
        perception_proc.terminate()
        print("[Sanitation] All processes terminated.")

if __name__ == "__main__":
    launch_sanitation()
