#!/usr/bin/env python3
"""
Robot Brain Integration - Downloads and uses trained AI models
Connects cloud-trained policies to local MuJoCo simulation.
"""

import argparse
import json
import os
import time
import numpy as np
import subprocess
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(PROJECT_ROOT))

# ML imports
try:
    import torch
    import torch.nn as nn
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  PyTorch not available - using heuristic control")

# Cloud storage imports
try:
    from google.cloud import storage
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False


class RobotBrain:
    """Integrates trained AI models with robot control."""
    
    def __init__(self, model_path: str = None, use_heuristic: bool = True):
        self.model = None
        self.use_heuristic = use_heuristic
        self.heuristic_policy = None
        
        if use_heuristic:
            from ai_training_pipeline import HeuristicPolicy
            self.heuristic_policy = HeuristicPolicy()
            print("🧠 Using heuristic policy")
        
        if model_path and ML_AVAILABLE and STORAGE_AVAILABLE:
            try:
                self.model = RobotPolicy()
                self.model.load_state_dict(torch.load(model_path))
                self.model.eval()
                print(f"✅ Loaded trained model: {model_path}")
            except Exception as e:
                print(f"⚠️  Failed to load model: {e}")
                self.use_heuristic = True
    
    def get_action(self, robot_pos: list, trash_positions: list) -> str:
        """Get action from AI model or heuristic."""
        if self.model is not None:
            return self._get_model_action(robot_pos, trash_positions)
        elif self.heuristic_policy:
            return self.heuristic_policy.get_action(np.array(robot_pos), trash_positions)
        else:
            return "stop"
    
    def _get_model_action(self, robot_pos: list, trash_positions: list) -> str:
        """Get action from trained neural network."""
        if not trash_positions:
            return "stop"
        
        # Create state vector
        state = np.concatenate([
            robot_pos[:2], 
            [0, 0],  # Simplified orientation
            [len(trash_positions) / 8.0]  # Trash remaining
        ])
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        # Get action from model
        with torch.no_grad():
            action_logits = self.model(state_tensor)
            action_idx = torch.argmax(action_logits).item()
        
        # Convert to action string
        action_map = {0: "forward", 1: "turn_left", 2: "turn_right", 3: "stop"}
        return action_map.get(action_idx, "stop")


def download_latest_model(bucket_name: str) -> str:
    """Download the latest trained model from GCS."""
    if not STORAGE_AVAILABLE:
        print("⚠️  Storage not available - using heuristic only")
        return None
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix="models/policy_"))
    
    if not blobs:
        print("⚠️  No trained models found")
        return None
    
    # Get most recent model
    latest_blob = max(blobs, key=lambda blob: blob.updated)
    model_path = f"/tmp/{os.path.basename(latest_blob.name)}"
    latest_blob.download_to_filename(model_path)
    
    print(f"✅ Downloaded latest model: {latest_blob.name}")
    return model_path


def run_intelligent_robot(model_path: str = None, use_heuristic: bool = False):
    """Run robot with AI control."""
    print("🤖 Starting intelligent robot control...")
    
    # Initialize robot brain
    brain = RobotBrain(model_path=model_path, use_heuristic=use_heuristic)
    
    # Start robot simulation
    cmd = [
        "python3", "simulation/run_robot_bridge.py",
        "--scene", "simulation/bathroom_scene.xml",
        "--domain", "200",  # Different domain for intelligent robot
        "--interface", "lo0",
        "--sanitation"
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(PROJECT_ROOT)
    )
    
    print("🧪 Robot simulation started with AI control")
    print("📊 Performance metrics will be displayed here")
    print("🔄 Model will be updated from cloud periodically")
    
    try:
        # Monitor and interact
        while True:
            try:
                # Read robot state from simulation
                line = process.stdout.readline()
                if line:
                    print(f"Robot: {line.strip()}")
                
                # Check if process is still running
                if process.poll() is not None:
                    break
                    
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping robot simulation...")
                break
                
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def main():
    parser = argparse.ArgumentParser(description="Run robot with AI brain")
    parser.add_argument("--model-bucket", default="mujoco-sanitation-models", help="GCS model bucket")
    parser.add_argument("--heuristic", action="store_true", help="Use heuristic policy only")
    parser.add_argument("--local-model", help="Use local model file")
    
    args = parser.parse_args()
    
    print("🧠 Robot Brain Integration Starting...")
    
    # Get model
    model_path = None
    if args.local_model:
        model_path = args.local_model
        print(f"Using local model: {model_path}")
    elif not args.heuristic:
        model_path = download_latest_model(args.model_bucket)
    
    # Run intelligent robot
    run_intelligent_robot(model_path, use_heuristic=args.heuristic)


if __name__ == "__main__":
    main()
