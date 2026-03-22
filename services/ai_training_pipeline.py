#!/usr/bin/env python3
"""
AI Model Training Pipeline for MuJoCo Bathroom Robot
Learns from cloud-generated episode data to improve robot behavior.
"""

import argparse
import json
import os
import time
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[0]
os.chdir(PROJECT_ROOT)

# ML imports
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    ML_AVAILABLE = True
    print("✅ PyTorch available for ML training")
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  PyTorch not available - using heuristic policies")

# Cloud storage imports
try:
    from google.cloud import storage
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False


class RobotPolicy(nn.Module):
    """Neural network policy for robot navigation and trash collection."""
    
    def __init__(self, state_dim=5, action_dim=4, hidden_dim=64, seq_len=50):
        super(RobotPolicy, self).__init__()
        self.seq_len = seq_len
        
        # LSTM for sequence processing
        self.lstm = nn.LSTM(state_dim, hidden_dim, batch_first=True)
        
        # Policy head
        self.policy_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Tanh()  # Bounded actions
        )
        
    def forward(self, state):
        """Forward pass through policy network."""
        # state shape: (batch_size, seq_len, state_dim)
        lstm_out, _ = self.lstm(state)
        
        # Use last output for action prediction
        if len(state.shape) == 3:  # (batch, seq, features)
            last_output = lstm_out[:, -1, :]  # Last time step
        else:  # (seq, features) - single sample
            last_output = lstm_out[-1, :]
        
        return self.policy_head(last_output)


class HeuristicPolicy:
    """Simple heuristic policy for trash collection."""
    
    def __init__(self):
        self.target_trash = None
        self.current_pos = np.array([1.93, 1.48])  # Start position
        
    def get_action(self, robot_pos, trash_positions):
        """Get action based on nearest trash."""
        if not trash_positions:
            return "stop"
        
        # Find nearest trash
        distances = [np.linalg.norm(robot_pos - np.array(trash)) for trash in trash_positions]
        nearest_idx = np.argmin(distances)
        nearest_trash = trash_positions[nearest_idx]
        
        # Calculate direction to trash
        direction = nearest_trash - robot_pos
        distance = distances[nearest_idx]
        
        # Action logic
        if distance < 0.5:  # Very close - collect
            return "collect"
        elif abs(direction[0]) > abs(direction[1]):  # More X than Y
            return "turn_right" if direction[0] > 0 else "turn_left"
        elif direction[1] > 0:  # Forward
            return "forward"
        else:
            return "backward"
    
    def update_position(self, new_pos):
        """Update current robot position."""
        self.current_pos = np.array(new_pos)


class TrainingDataset(Dataset):
    """Dataset for robot training episodes."""
    
    def __init__(self, episode_files):
        self.episodes = []
        for file in episode_files:
            with open(file, 'r') as f:
                self.episodes.append(json.load(f))
    
    def __len__(self):
        return len(self.episodes)
    
    def __getitem__(self, idx):
        episode = self.episodes[idx]
        states = []
        actions = []
        
        for step in episode["steps"]:
            # Create state vector [robot_pos, robot_orientation, trash_remaining]
            robot_pos = step["robot_position"][:2]
            robot_orientation = step["robot_orientation"][:2] 
            trash_remaining = step["trash_remaining"]
            
            # State vector with 5 dimensions
            state = robot_pos + robot_orientation + [trash_remaining / 8.0]
            
            # Convert action to one-hot
            action_map = {"forward": 0, "turn_left": 1, "turn_right": 2, "stop": 3, "collect": 4}
            action_idx = action_map.get(step["action"], 0)
            
            states.append(state)
            actions.append(action_idx)
        
        # Pad sequences to same length for batching
        if len(states) > 0:
            max_len = 50  # Max sequence length
            if len(states) < max_len:
                # Pad sequences
                last_state = states[-1] if states else [0] * 8
                last_action = actions[-1] if actions else 0
                states.extend([last_state] * (max_len - len(states)))
                actions.extend([last_action] * (max_len - len(actions)))
            else:
                states = states[:max_len]
                actions = actions[:max_len]
        
        return torch.FloatTensor(states), torch.LongTensor(actions)


def download_training_data(bucket_name: str) -> List[str]:
    """Download training data from GCS."""
    if not STORAGE_AVAILABLE:
        print("⚠️  Storage not available - using local data")
        return []
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix="episodes/"))
    
    episode_files = []
    local_dir = "/tmp/training_episodes"
    os.makedirs(local_dir, exist_ok=True)
    
    for blob in blobs:
        if blob.name.endswith('.json'):
            local_path = f"{local_dir}/{os.path.basename(blob.name)}"
            blob.download_to_filename(local_path)
            episode_files.append(local_path)
            print(f"Downloaded {blob.name} to {local_path}")
    
    return episode_files


def train_policy_model(episode_files: str, epochs: int = 50):
    """Train neural network policy on episode data."""
    if not ML_AVAILABLE:
        print("⚠️  ML not available - skipping training")
        return None
    
    print(f"🧠 Training policy on {len(episode_files)} episodes...")
    
    # Create dataset
    dataset = TrainingDataset(episode_files)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Initialize model
    model = RobotPolicy()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    for epoch in range(epochs):
        total_loss = 0
        for batch_idx, (states, actions) in enumerate(dataloader):
            # Reshape for sequence data: (batch, seq, features) -> (batch*seq, features)
            batch_size, seq_len, state_dim = states.shape
            states_flat = states.view(batch_size * seq_len, state_dim)
            actions_flat = actions.view(batch_size * seq_len)
            
            optimizer.zero_grad()
            outputs = model(states_flat)
            loss = criterion(outputs, actions_flat)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
    
    return model


def evaluate_policy(model, test_episodes: int = 10):
    """Evaluate trained policy on test episodes."""
    print(f"🧪 Evaluating policy on {test_episodes} test episodes...")
    
    success_count = 0
    total_steps = 0
    
    for episode in range(test_episodes):
        # Simulate episode with trained policy
        success, steps = simulate_episode_with_policy(model)
        if success:
            success_count += 1
        total_steps += steps
    
    success_rate = success_count / test_episodes
    avg_steps = total_steps / test_episodes
    
    print(f"📊 Evaluation Results:")
    print(f"  Success Rate: {success_rate:.1%}")
    print(f"  Average Steps: {avg_steps:.1f}")
    
    return success_rate, avg_steps


def simulate_episode_with_policy(model, max_steps: int = 200):
    """Simulate one episode using trained policy."""
    # Simplified simulation - in real implementation would use actual robot bridge
    robot_pos = np.array([1.93, 1.48])  # Start position
    trash_positions = [
        [4.81, 4.77], [2.39, 4.03], [1.93, 1.48],
        [4.33, 3.43], [2.59, 1.54], [4.36, 4.18],
        [1.44, 4.23], [2.37, 4.49]
    ]
    trash_collected = 0
    
    for step in range(max_steps):
        # Create state vector
        state = np.concatenate([
            robot_pos[:2], 
            [0, 0],  # Simplified orientation
            [len(trash_positions) / 8.0]  # Trash remaining
        ])
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        
        # Get action from policy
        with torch.no_grad():
            action_logits = model(state_tensor)
            action_idx = torch.argmax(action_logits).item()
        
        # Convert to action
        action_map = {0: "forward", 1: "turn_left", 2: "turn_right", 3: "stop"}
        action = action_map.get(action_idx, "stop")
        
        # Execute action (simplified)
        if action == "forward":
            robot_pos[1] += 0.1
        elif action == "turn_left":
            robot_pos[0] -= 0.1
        elif action == "turn_right":
            robot_pos[0] += 0.1
        
        # Check trash collection
        for i, trash_pos in enumerate(trash_positions):
            if np.linalg.norm(robot_pos - np.array(trash_pos)) < 0.3:
                trash_positions.pop(i)
                trash_collected += 1
                break
        
        if trash_collected >= 8:
            return True, step + 1
    
    return False, max_steps


def upload_model_to_gcs(model, bucket_name: str):
    """Upload trained model to GCS."""
    if not STORAGE_AVAILABLE:
        print("⚠️  Storage not available - skipping model upload")
        return
    
    # Save model
    model_path = "/tmp/trained_policy.pt"
    torch.save(model.state_dict(), model_path)
    
    # Upload to GCS
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"models/policy_{int(time.time())}.pt")
    blob.upload_from_filename(model_path)
    print(f"✅ Model uploaded to gs://{bucket_name}/models/policy_{int(time.time())}.pt")


def main():
    parser = argparse.ArgumentParser(description="Train AI policy for robot")
    parser.add_argument("--episodes", type=int, default=100, help="Training episodes to use")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--gcs-bucket", default="mujoco-sanitation-data", help="GCS data bucket")
    parser.add_argument("--model-bucket", default="mujoco-sanitation-models", help="GCS model bucket")
    parser.add_argument("--download-only", action="store_true", help="Only download data, no training")
    parser.add_argument("--local-only", action="store_true", help="Use local data only")
    
    args = parser.parse_args()
    
    print("🤖 Starting AI Training Pipeline")
    
    # Get training data
    if args.local_only:
        episode_files = [f"/tmp/training_data/episode_{i:04d}.json" for i in range(args.episodes)]
    else:
        episode_files = download_training_data(args.gcs_bucket)
    
    if not episode_files:
        print("❌ No training data found")
        return
    
    if args.download_only:
        print(f"✅ Downloaded {len(episode_files)} episodes")
        return
    
    # Train model
    model = train_policy_model(episode_files, args.epochs)
    
    if model is None:
        print("❌ Training failed")
        return
    
    # Evaluate model
    success_rate, avg_steps = evaluate_policy(model)
    
    # Upload model
    upload_model_to_gcs(model, args.model_bucket)
    
    print(f"🎉 Training completed!")
    print(f"📈 Success Rate: {success_rate:.1%}")
    print(f"⚡ Average Steps: {avg_steps:.1f}")


if __name__ == "__main__":
    main()
