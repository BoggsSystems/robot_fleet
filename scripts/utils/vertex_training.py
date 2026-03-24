#!/usr/bin/env python3
"""
Vertex AI training job configuration for MuJoCo robot training.
"""

import os
from google.cloud import aiplatform

def create_training_job():
    """Create and run a Vertex AI training job."""
    
    # Initialize Vertex AI
    aiplatform.init(
        project="mujoco-sanitation-ai",
        location="us-central1",
        staging_bucket="gs://mujoco-sanitation-data"
    )
    
    # Training job configuration
    job = aiplatform.CustomJob(
        display_name="mujoco-robot-training",
        container_image_uri="us-central1-docker.pkg.dev/mujoco-sanitation-ai/mujoco-training/mujoco-simulation:latest",
        command=["python3", "cloud_training.py"],
        args=[
            "--episodes", "50",
            "--max-steps", "1000", 
            "--output-dir", "/tmp/training_data",
            "--gcs-bucket", "mujoco-sanitation-data",
            "--upload"
        ],
        machine_type="n1-standard-8",
        accelerator_type="NVIDIA_TESLA_T4",
        accelerator_count=1,
        boot_disk_size_gb=200
    )
    
    print("Submitting training job to Vertex AI...")
    job.run()
    
    print(f"✅ Training job submitted: {job.display_name}")
    print(f"Job ID: {job.name}")
    print(f"View in console: https://console.cloud.google.com/ai/platform/trainings/{job.name}")
    
    return job

if __name__ == "__main__":
    create_training_job()
