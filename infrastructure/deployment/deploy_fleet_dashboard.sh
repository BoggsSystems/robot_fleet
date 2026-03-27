#!/bin/bash

# Fleet Dashboard Deployment Script
echo "🚀 Deploying Fleet Dashboard"

# Set variables
FLEET_DASHBOARD_DIR="../frontend/web/fleet_dashboard"
IMAGE_NAME="fleet-dashboard"
CONTAINER_NAME="fleet-dashboard-prod"
PORT="3000"

# Build the Docker image
echo "📦 Building Fleet Dashboard image..."
cd "$FLEET_DASHBOARD_DIR"
docker build -t $IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"

# Stop and remove existing container
echo "🛑 Stopping existing container..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Run the new container
echo "🚀 Starting Fleet Dashboard container..."
docker run -d \
  --name $CONTAINER_NAME \
  -p $PORT:80 \
  -e NODE_ENV=production \
  -e REACT_APP_AUTH_URL=https://robotfleet-auth.kindmoss-6eac8399.eastus.azurecontainerapps.io \
  -e REACT_APP_API_URL=https://robotfleet-ai.kindmoss-6eac8399.eastus.azurecontainerapps.io \
  --restart unless-stopped \
  $IMAGE_NAME

if [ $? -ne 0 ]; then
    echo "❌ Container start failed"
    exit 1
fi

echo "✅ Fleet Dashboard deployed successfully!"
echo "🌐 Fleet Dashboard is available at: http://localhost:$PORT"

# Wait a moment and check health
echo "🏥 Checking container health..."
sleep 5

if curl -s -f http://localhost:$PORT > /dev/null; then
    echo "✅ Fleet Dashboard is responding correctly"
else
    echo "⚠️  Fleet Dashboard may not be responding correctly"
fi

echo "📋 Deployment Summary:"
echo "   - Image: $IMAGE_NAME"
echo "   - Container: $CONTAINER_NAME"
echo "   - Port: $PORT"
echo "   - URL: http://localhost:$PORT"
