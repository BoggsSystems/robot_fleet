#!/bin/bash

# Deploy Auth Service to Azure Container App
echo "🚀 Deploying Auth Service to Azure Container App"

# Configuration
RESOURCE_GROUP="robot-fleet-simulator-rg"
LOCATION="eastus"
CONTAINER_APP_NAME="robotfleet-auth"
REGISTRY="robotfleetregistry.azurecr.io"
IMAGE_NAME="auth-csharp"
TAG="latest"
ACR_USERNAME=$(az acr credential show --name robotfleetregistry --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name robotfleetregistry --query passwords[0].value --output tsv)

# Build and push Docker image
echo "📦 Building Docker image..."
cd /Users/jeffboggs/robot_fleet/backend/services/auth_csharp

# Build using Docker locally with correct platform
docker build --platform linux/amd64 -t ${REGISTRY}/${IMAGE_NAME}:${TAG} .

echo "📤 Pushing Docker image to ACR..."
docker push ${REGISTRY}/${IMAGE_NAME}:${TAG}

if [ $? -ne 0 ]; then
    echo "❌ Docker push failed"
    exit 1
fi

echo "✅ Docker image pushed successfully"

# Deploy to Container App
echo "🚀 Deploying to Container App..."

az containerapp up \
    --name ${CONTAINER_APP_NAME} \
    --resource-group ${RESOURCE_GROUP} \
    --location ${LOCATION} \
    --image ${REGISTRY}/${IMAGE_NAME}:${TAG} \
    --target-port 3001 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 2 \
    --cpu 0.5 \
    --memory 1Gi \
    --registry-server ${REGISTRY} \
    --registry-username ${ACR_USERNAME} \
    --registry-password ${ACR_PASSWORD}

if [ $? -ne 0 ]; then
    echo "❌ Container App deployment failed"
    exit 1
fi

echo "✅ Container App deployed successfully!"

# Get the app URL
APP_URL=$(az containerapp show \
    --name ${CONTAINER_APP_NAME} \
    --resource-group ${RESOURCE_GROUP} \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

echo "🌐 Auth Service is available at: https://${APP_URL}"

echo "🎉 Auth Service deployment completed!"
