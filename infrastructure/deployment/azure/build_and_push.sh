#!/bin/bash
# Build and push Docker image to Google Artifact Registry

set -e

# Configuration
PROJECT_ID="mujoco-sanitation-ai"
REPO_NAME="mujoco-training"
IMAGE_NAME="mujoco-simulation"
IMAGE_TAG="latest"
REGION="us-central1"

# Full image path
IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building Docker image for MuJoCo simulation..."
echo "Image path: ${IMAGE_PATH}"

# Build the Docker image
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

# Tag for Artifact Registry
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_PATH}

# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker ${REGION}.docker.pkg.dev

# Push to Artifact Registry
echo "Pushing image to Artifact Registry..."
docker push ${IMAGE_PATH}

echo "✅ Image successfully pushed to: ${IMAGE_PATH}"
echo "Image can now be used in Vertex AI training jobs or Compute Engine instances"
