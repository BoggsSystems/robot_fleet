import subprocess
import os
import sys
import time

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VENV_PYTHON = os.path.join(REPO_ROOT, "venv", "bin", "python3")
MJPYTHON = os.path.join(REPO_ROOT, "venv", "bin", "mjpython")
PYTHON = MJPYTHON if os.path.exists(MJPYTHON) else VENV_PYTHON
RUNNER = os.path.join(REPO_ROOT, "simulation", "run_robot_bridge.py")
SCENE = os.path.join(REPO_ROOT, "SDK/unitree_mujoco/unitree_robots/g1/box_training_scene.xml")

def main():
    print("[Scenario] Launching Box Inspection Training Scenario...")
    
    # 1. Start the bridge for Robot 0 (Domain 100) with the training scene
    cmd = [
        PYTHON, RUNNER,
        "--scene", SCENE,
        "--domain", "100",
        "--interface", "lo0"
    ]
    env = os.environ.copy()
    env["CYCLONEDDS_HOME"] = os.path.expanduser("~/cyclonedds/install")
    
    bridge_proc = subprocess.Popen(cmd, env=env)
    
    time.sleep(2) # Wait for bridge to init
    
    # 2. Start the Vision Bridge (Simulation of Camera)
    vision_src = os.path.join(REPO_ROOT, "simulation", "vision_bridge.py")
    vision_proc = subprocess.Popen([VENV_PYTHON, vision_src, "--scene", SCENE, "--domain", "100"])

    # 3. Start the Perception Service (AI Processing)
    perception_src = os.path.join(REPO_ROOT, "perception", "perception_service.py")
    perception_proc = subprocess.Popen([VENV_PYTHON, perception_src, "100"])

    print("\n[Scenario] Running! Focus the MuJoCo window to see the robot looking at the box.")
    print("[Scenario] The AI will output detections in this terminal.")
    print("[Scenario] Press Ctrl+C to stop.")

    try:
        bridge_proc.wait()
    except KeyboardInterrupt:
        bridge_proc.terminate()
        vision_proc.terminate()
        perception_proc.terminate()

if __name__ == "__main__":
    main()
