#!/bin/bash

# Simple Azure Deployment using base images
# No Docker build required

set -e

echo "🚀 Simple Azure Deployment - No Docker Build Required"

# Variables
RESOURCE_GROUP="robot-fleet-simulator-rg"
ENVIRONMENT="robot-fleet-env"

echo ""
echo "📋 Step 1: Deploy C# Digital Twin Service (using .NET base image)..."

# Deploy C# service using base image
az containerapp create \
    --name warehouse-digital-twin \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image mcr.microsoft.com/dotnet/aspnet:8.0 \
    --cpu 1 \
    --memory 2Gi \
    --ingress external \
    --target-port 80

echo ""
echo "📋 Step 2: Deploy Python AI Engine (using Python base image)..."

# Deploy Python service using base image
az containerapp create \
    --name warehouse-ai-engine \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image python:3.9-slim \
    --cpu 2 \
    --memory 4Gi \
    --ingress external \
    --target-port 8000

echo ""
echo "📋 Step 3: Deploy Integration Hub (using Python base image)..."

# Deploy Integration Hub using base image
az containerapp create \
    --name warehouse-integration-hub \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image python:3.9-slim \
    --cpu 1.5 \
    --memory 3Gi \
    --ingress external \
    --target-port 9000

echo ""
echo "✅ Basic deployment complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Check service URLs below"
echo "2. Test basic connectivity"
echo "3. Later update with custom images when Docker is working"

# Get service URLs
DIGITAL_TWIN_URL=$(az containerapp show \
    --name warehouse-digital-twin \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

AI_ENGINE_URL=$(az containerapp show \
    --name warehouse-ai-engine \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

INTEGRATION_HUB_URL=$(az containerapp show \
    --name warehouse-integration-hub \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

echo ""
echo "📋 Service URLs:"
echo "🏭 Digital Twin: https://$DIGITAL_TWIN_URL"
echo "🧠 AI Engine: https://$AI_ENGINE_URL"
echo "🔄 Integration Hub: https://$INTEGRATION_HUB_URL"
