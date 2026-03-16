import subprocess
import time
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VENV_PYTHON = os.path.join(REPO_ROOT, "venv/bin/python3")
MJ_PYTHON = os.path.join(REPO_ROOT, "venv/bin/mjpython")

# Scene path
SCENE = os.path.join(REPO_ROOT, "SDK/unitree_mujoco/unitree_robots/g1/inventory_sweep_scene.xml")

def launch():
    print("[Scenario] Launching Inventory Sweep Scenario...")
    
    # 1. Start the Robot Bridge (Physics)
    bridge_src = os.path.join(REPO_ROOT, "simulation", "run_robot_bridge.py")
    bridge_proc = subprocess.Popen([MJ_PYTHON, bridge_src, "--scene", SCENE, "--domain", "100", "--sweep"])
    
    time.sleep(3) # Wait for bridge to init
    
    # 2. Start the Vision Bridge (Headless Camera)
    vision_src = os.path.join(REPO_ROOT, "simulation", "vision_bridge.py")
    vision_proc = subprocess.Popen([VENV_PYTHON, vision_src, "--scene", SCENE, "--domain", "100"])

    # 3. Start the Perception Service (AI Processing)
    perception_src = os.path.join(REPO_ROOT, "perception", "perception_service.py")
    perception_proc = subprocess.Popen([VENV_PYTHON, perception_src, "100"])

    print("\n[Scenario] Running! Robot is in the 10m aisle.")
    print("[Scenario] The AI is monitoring the feed.")
    print("[Scenario] Press Ctrl+C to stop.")

    try:
        # Keep main thread alive
        bridge_proc.wait()
    except KeyboardInterrupt:
        print("\n[Scenario] Shutting down...")
        bridge_proc.terminate()
        vision_proc.terminate()
        perception_proc.terminate()

if __name__ == "__main__":
    launch()
