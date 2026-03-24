#!/usr/bin/env python3
"""
Simple Working AI Training - Avoids tensor dimension issues
"""

import argparse
import json
import os
import time
import numpy as np
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[0]
os.chdir(PROJECT_ROOT)

# ML imports
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    ML_AVAILABLE = True
    print("✅ PyTorch available for ML training")
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  PyTorch not available - using simple statistics")

class SimplePolicy:
    """Simple policy based on training data statistics."""
    
    def __init__(self):
        self.action_counts = {"forward": 0, "turn_left": 0, "turn_right": 0, "stop": 0}
        self.state_action_map = {}
        
    def train(self, episodes):
        """Train simple policy from episode data."""
        print("🧠 Training simple policy from episodes...")
        
        # Analyze training data
        for episode in episodes:
            for step in episode["steps"]:
                state_key = self._get_state_key(step)
                action = step["action"]
                
                if state_key not in self.state_action_map:
                    self.state_action_map[state_key] = {"forward": 0, "turn_left": 0, "turn_right": 0, "stop": 0}
                
                self.state_action_map[state_key][action] += 1
        
        print("✅ Policy training completed!")
        
    def _get_state_key(self, step):
        """Create simple state key from robot position."""
        robot_pos = step["robot_position"][:2]
        trash_remaining = step["trash_remaining"]
        
        # Simple discretization
        x_zone = "left" if robot_pos[0] < 2.0 else "right"
        y_zone = "bottom" if robot_pos[1] < 2.0 else "top"
        trash_zone = "high" if trash_remaining > 4 else "low"
        
        return f"{x_zone}_{y_zone}_{trash_zone}"
    
    def get_action(self, robot_pos, trash_remaining):
        """Get action based on trained policy."""
        x_zone = "left" if robot_pos[0] < 2.0 else "right"
        y_zone = "bottom" if robot_pos[1] < 2.0 else "top"
        trash_zone = "high" if trash_remaining > 4 else "low"
        state_key = f"{x_zone}_{y_zone}_{trash_zone}"
        
        if state_key in self.state_action_map:
            actions = list(self.state_action_map[state_key].keys())
            counts = list(self.state_action_map[state_key].values())
            
            if sum(counts) > 0:
                # Choose action with highest probability
                best_action = actions[np.argmax(counts)]
                return best_action
        
        return "stop"


def train_simple_model(episodes, epochs=10):
    """Train a simple statistical model."""
    if not ML_AVAILABLE:
        print("⚠️  Using statistical training (no PyTorch)")
        return SimplePolicy()
    
    print("🧠 Training neural network policy...")
    
    # Create simple neural network
    model = nn.Sequential(
        nn.Linear(5, 32),  # 5D state -> 32 hidden
        nn.ReLU(),
        nn.Linear(32, 16),
        nn.ReLU(),
        nn.Linear(16, 4),  # 4 actions
        nn.Softmax(dim=-1)
    )
    
    # Simple training data
    states = []
    actions = []
    
    for episode in episodes:
        for step in episode["steps"]:
            robot_pos = step["robot_position"][:2]
            trash_remaining = step["trash_remaining"]
            
            # 5D state vector
            state = np.array([
                robot_pos[0], robot_pos[1],  # position
                1.0 if robot_pos[0] < 2.0 else 0.0,  # left/right
                1.0 if robot_pos[1] < 2.0 else 0.0,  # bottom/top
                trash_remaining / 8.0  # trash level
            ])
            
            # Action to one-hot
            action_map = {"forward": 0, "turn_left": 1, "turn_right": 2, "stop": 3}
            action_idx = action_map.get(step["action"], 0)
            
            states.append(state)
            actions.append(action_idx)
    
    # Train for a few epochs
    states_tensor = torch.FloatTensor(states)
    actions_tensor = torch.LongTensor(actions)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    
    print(f"Training on {len(episodes)} episodes for {epochs} epochs...")
    
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(states_tensor)
        loss = criterion(outputs, actions_tensor)
        loss.backward()
        optimizer.step()
        
        print(f"  Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
    
    return model


def evaluate_model(model, episodes):
    """Evaluate model performance."""
    print("🧪 Evaluating model performance...")
    
    correct = 0
    total = len(episodes) * 20  # Approximate steps per episode
    
    for episode in episodes:
        for step in episode["steps"][:10]:  # Test first 10 steps
            robot_pos = step["robot_position"][:2]
            trash_remaining = step["trash_remaining"]
            
            state = torch.FloatTensor([
                robot_pos[0], robot_pos[1],
                1.0 if robot_pos[0] < 2.0 else 0.0,
                1.0 if robot_pos[1] < 2.0 else 0.0,
                trash_remaining / 8.0
            ])
            
            with torch.no_grad():
                output = model(state)
                predicted_action = torch.argmax(output).item()
            
            action_map = {"forward": 0, "turn_left": 1, "turn_right": 2, "stop": 3}
            expected_action = action_map.get(step["action"], 0)
            
            if predicted_action == expected_action:
                correct += 1
    
    accuracy = correct / total
    print(f"✅ Model accuracy: {accuracy:.1%}")
    
    return accuracy


def main():
    parser = argparse.ArgumentParser(description="Simple AI training")
    parser.add_argument("--episodes", type=int, default=20, help="Training episodes")
    parser.add_argument("--epochs", type=int, default=10, help="Training epochs")
    parser.add_argument("--local-only", action="store_true", help="Use local data only")
    
    args = parser.parse_args()
    
    print("🤖 Simple AI Training Pipeline")
    
    # Load episode data
    episode_files = [f"/tmp/training_data/episode_{i:04d}.json" for i in range(args.episodes)]
    
    if not episode_files:
        print("❌ No training data found")
        return
    
    # Train model
    model = train_simple_model(episode_files, args.epochs)
    
    # Evaluate
    accuracy = evaluate_model(model, episode_files)
    
    # Save model
    if ML_AVAILABLE:
        model_path = "/tmp/simple_trained_model.pt"
        torch.save(model.state_dict(), model_path)
        print(f"✅ Model saved to: {model_path}")
    
    print(f"\n🎉 Training Completed!")
    print(f"📈 Model Accuracy: {accuracy:.1%}")
    print(f"📁 Trained on {args.episodes} episodes for {args.epochs} epochs")


if __name__ == "__main__":
    main()
