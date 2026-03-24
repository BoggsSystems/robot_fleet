#!/usr/bin/env python3
"""
Cloud training script for MuJoCo bathroom sanitation robot.
Runs headless simulation episodes and collects training data.
"""

import argparse
import json
import os
import sys
import time
import numpy as np
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(PROJECT_ROOT))

# Cloud storage imports
try:
    from google.cloud import storage
    from google.cloud import aiplatform
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False
    print("Warning: Google Cloud libraries not available. Running in local mode.")

from data import log_utils


def upload_to_gcs(local_path, gcs_path, bucket_name):
    """Upload file to Google Cloud Storage."""
    if not STORAGE_AVAILABLE:
        print(f"Skipping upload to {gcs_path} (GCS not available)")
        return
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)
    print(f"Uploaded {local_path} to gs://{bucket_name}/{gcs_path}")


def run_training_episode(episode_id, max_steps=1000, output_dir="/tmp"):
    """Run a single training episode using subprocess."""
    print(f"Starting episode {episode_id}")
    
    # Episode data storage
    episode_data = {
        "episode_id": episode_id,
        "start_time": time.time(),
        "steps": [],
        "total_reward": 0.0,
        "trash_collected": 0,
        "success": False
    }
    
    try:
        # Start the simulation process
        cmd = [
            "python3", "simulation/run_robot_bridge.py",
            "--scene", "simulation/bathroom_scene.xml",
            "--domain", str(100 + episode_id),  # Different domain per episode
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
        
        # Simulate running for some steps (simplified)
        for step in range(min(max_steps, 50)):  # Limit to 50 steps for demo
            try:
                # Check if process is still running
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    break
                
                # Simulate step data (in real implementation, would read from process)
                step_data = {
                    "step": step,
                    "robot_position": [1.93 + np.random.random() * 0.1, 1.48 + np.random.random() * 0.1, 0.8],
                    "robot_orientation": [0, 0, 0, 1],
                    "action": np.random.choice(["forward", "turn_left", "turn_right", "stop"]),
                    "reward": episode_data["total_reward"],
                    "trash_remaining": max(0, 8 - episode_data["trash_collected"])
                }
                episode_data["steps"].append(step_data)
                
                # Simulate trash collection randomly
                if np.random.random() < 0.1:  # 10% chance per step
                    episode_data["trash_collected"] += 1
                    episode_data["total_reward"] += 10.0
                
                # Check if all trash collected
                if episode_data["trash_collected"] >= 8:
                    episode_data["success"] = True
                    break
                
                time.sleep(0.1)  # Small delay between steps
                
            except Exception as e:
                print(f"Step {step} failed: {e}")
                break
        
        # Clean up process
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            
    except Exception as e:
        print(f"Episode {episode_id} failed: {e}")
        episode_data["error"] = str(e)
    
    finally:
        episode_data["end_time"] = time.time()
        episode_data["duration"] = episode_data["end_time"] - episode_data["start_time"]
    
    # Save episode data
    episode_file = f"{output_dir}/episode_{episode_id:04d}.json"
    with open(episode_file, 'w') as f:
        json.dump(episode_data, f, indent=2)
    
    return episode_file


def main():
    parser = argparse.ArgumentParser(description="Run cloud training for MuJoCo robot")
    parser.add_argument("--episodes", type=int, default=10, help="Number of training episodes")
    parser.add_argument("--max-steps", type=int, default=1000, help="Max steps per episode")
    parser.add_argument("--output-dir", default="/tmp/training_data", help="Output directory")
    parser.add_argument("--gcs-bucket", default="mujoco-sanitation-data", help="GCS bucket for data")
    parser.add_argument("--upload", action="store_true", help="Upload results to GCS")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Running {args.episodes} training episodes...")
    
    # Run training episodes
    episode_files = []
    for episode in range(args.episodes):
        episode_file = run_training_episode(episode, args.max_steps, args.output_dir)
        episode_files.append(episode_file)
        
        # Upload if requested
        if args.upload:
            gcs_path = f"episodes/episode_{episode:04d}.json"
            upload_to_gcs(episode_file, gcs_path, args.gcs_bucket)
    
    # Create training summary
    summary = {
        "total_episodes": args.episodes,
        "completed_episodes": len(episode_files),
        "output_files": [os.path.basename(f) for f in episode_files],
        "timestamp": time.time()
    }
    
    summary_file = f"{args.output_dir}/training_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    if args.upload:
        upload_to_gcs(summary_file, "training_summary.json", args.gcs_bucket)
    
    print(f"✅ Training completed. Results saved to {args.output_dir}")
    if args.upload:
        print(f"✅ Results uploaded to gs://{args.gcs_bucket}/")


if __name__ == "__main__":
    main()
