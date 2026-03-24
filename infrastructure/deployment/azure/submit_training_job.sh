#!/bin/bash
# Submit Vertex AI training job using gcloud CLI

set -e

PROJECT_ID="mujoco-sanitation-ai"
REGION="us-central1"
IMAGE_URI="us-central1-docker.pkg.dev/mujoco-sanitation-ai/mujoco-training/mujoco-simulation:latest"
JOB_NAME="mujoco-robot-training-$(date +%Y%m%d-%H%M%S)"

echo "Submitting Vertex AI training job: ${JOB_NAME}"

gcloud ai custom-jobs create \
  --display-name="${JOB_NAME}" \
  --region="${REGION}" \
  --container-image-uri="${IMAGE_URI}" \
  --command="python3" \
  --args="cloud_training.py,--episodes,20,--max-steps,500,--output-dir,/tmp/training_data,--gcs-bucket,mujoco-sanitation-data,--upload" \
  --machine-type="n1-standard-4" \
  --accelerator-type="NVIDIA_TESLA_T4" \
  --accelerator-count=1 \
  --boot-disk-size-gb=100

echo "✅ Training job submitted successfully!"
echo "View jobs: https://console.cloud.google.com/ai/platform/custom-jobs?project=${PROJECT_ID}"
