#!/bin/bash

# Auth Service Deployment Script for Azure Container Apps
set -e

# Configuration
REGISTRY="robotfleetregistry.azurecr.io"
IMAGE_NAME="auth-csharp"
TAG="latest"
RESOURCE_GROUP="robot-fleet-simulator-rg"
CONTAINER_APP_NAME="robotfleet-auth"
ACR_USERNAME=$(az acr credential show --name $REGISTRY --query username --output tsv --query "[].username" | tr -d '\n')
ACR_PASSWORD=$(az acr credential show --name $REGISTRY --query password --output tsv --query "[].passwords[0].value" | tr -d '\n')

echo "🔨 Building and pushing Docker image..."

# Build using Docker locally with correct platform
cd ../../../backend/services/auth_csharp
docker build --platform linux/amd64 -t ${REGISTRY}/${IMAGE_NAME}:${TAG} .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

# Push to ACR
docker push ${REGISTRY}/${IMAGE_NAME}:${TAG}

if [ $? -ne 0 ]; then
    echo "❌ Docker push failed"
    exit 1
fi

echo "✅ Docker image pushed successfully"

# Deploy to Container App
echo "🚀 Deploying to Container App..."

# Update existing Container App
az containerapp update \
    --name ${CONTAINER_APP_NAME} \
    --resource-group ${RESOURCE_GROUP} \
    --image ${REGISTRY}/${IMAGE_NAME}:${TAG} \
    --cpu 0.5 \
    --memory 1Gi \
    --min-replicas 1 \
    --max-replicas 2 \
    --set-env-vars "DEPLOYMENT_FIX=$(date +%s)"

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

# Deployment Summary
echo "📋 Deployment Summary:"
echo "   - Container App: ${CONTAINER_APP_NAME}"
echo "   - Resource Group: ${RESOURCE_GROUP}"
echo "   - Location: eastus"
echo "   - Image: ${REGISTRY}/${IMAGE_NAME}:${TAG}"
echo "   - URL: https://${APP_URL}"
echo "   - Replicas: 1-2 (auto-scaling)"

echo "🔗 Next Steps:"
echo "   1. Visit https://${APP_URL} to verify deployment"
echo "   2. Check Azure Portal for monitoring and scaling"
echo "   3. Configure custom domain if needed"
echo "   4. Set up SSL certificate for custom domain"
