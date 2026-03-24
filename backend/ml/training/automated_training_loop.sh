#!/bin/bash
# Automated Cloud Training Loop
# Continuously trains robot AI and updates local robot with new models

set -e

PROJECT_ID="mujoco-sanitation-ai"
DATA_BUCKET="mujoco-sanitation-data"
MODEL_BUCKET="mujoco-sanitation-models"
TRAINING_EPISODES=50
TRAINING_EPOCHS=20

echo "🚀 Starting Automated Cloud Training Loop..."

while true; do
    echo ""
    echo "🔄 Training Cycle: $(date)"
    echo "=================================="
    
    # Step 1: Generate training data in cloud
    echo "📊 Step 1: Submitting cloud training job..."
    ./submit_training_job.sh
    
    if [ $? -ne 0 ]; then
        echo "❌ Training job submission failed"
        sleep 60
        continue
    fi
    
    # Wait for training to complete
    echo "⏱️  Waiting for training completion (10 minutes)..."
    sleep 600
    
    # Step 2: Train AI model on new data
    echo "🧠 Step 2: Training AI model..."
    python3 ai_training_pipeline.py \
        --episodes $TRAINING_EPISODES \
        --epochs $TRAINING_EPOCHS \
        --gcs-bucket $DATA_BUCKET \
        --model-bucket $MODEL_BUCKET
    
    if [ $? -ne 0 ]; then
        echo "❌ AI training failed"
        sleep 60
        continue
    fi
    
    # Step 3: Run robot with new brain
    echo "🤖 Step 3: Running robot with updated AI brain..."
    python3 robot_brain.py --model-bucket $MODEL_BUCKET &
    ROBOT_PID=$!
    
    # Run for testing period
    echo "🧪 Testing new model for 5 minutes..."
    sleep 300
    
    # Stop robot
    echo "🛑 Stopping robot for next cycle..."
    kill $ROBOT_PID 2>/dev/null
    wait $ROBOT_PID 2>/dev/null
    
    echo "✅ Training cycle completed"
    echo "💡 Next cycle starting in 1 hour..."
    sleep 3600
    
done
