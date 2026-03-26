#!/bin/bash

# Focused deployment script for Auth Service and Admin Webapp
# This fixes the failed services without redeploying working backend services

set -e

# Navigate to project root
cd /Users/jeffboggs/robot_fleet

echo "🔧 Fixing failed Azure services..."
echo "📍 Resource group: robot-fleet-simulator-rg"
echo ""

# Variables
RESOURCE_GROUP="robot-fleet-simulator-rg"
ENVIRONMENT="robot-fleet-env"
REGISTRY="robotfleetregistry.azurecr.io"

echo "📋 Step 1: Logging into Azure Container Registry..."
az acr login --name robotfleetregistry

echo ""
echo "📋 Step 2: Building Auth Service..."
cd backend/services/auth_csharp
docker build -t $REGISTRY/warehouse-auth-service:latest .
docker push $REGISTRY/warehouse-auth-service:latest
cd ../../../

echo ""
echo "📋 Step 3: Building Admin Web Dashboard..."
cd frontend/web/admin_dashboard

# Get auth service URL for build (may not exist yet, use fallback)
AUTH_URL=$(az containerapp show \
    --name warehouse-auth-service \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv 2>/dev/null || echo "warehouse-auth-service.kindmoss-6eac8399.eastus.azurecontainerapps.net")

docker build \
    --platform linux/amd64 \
    --build-arg REACT_APP_AUTH_URL=https://$AUTH_URL \
    -t $REGISTRY/admin-webapp:latest .
docker push $REGISTRY/admin-webapp:latest
cd ../../../

echo ""
echo "📋 Step 3: Deploying Auth Service..."
az containerapp create \
    --name warehouse-auth-service \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image $REGISTRY/warehouse-auth-service:latest \
    --cpu 0.5 \
    --memory 1Gi \
    --env-vars \
        ASPNETCORE_ENVIRONMENT="Production" \
    --ingress external \
    --target-port 3001

echo ""
echo "📋 Step 4: Deploying Admin Web Dashboard..."
az containerapp create \
    --name admin-webapp \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image $REGISTRY/admin-webapp:latest \
    --cpu 0.5 \
    --memory 1Gi \
    --ingress external \
    --target-port 80

echo ""
echo "📋 Step 5: Getting service URLs..."

AUTH_SERVICE_URL=$(az containerapp show \
    --name warehouse-auth-service \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

ADMIN_WEBAPP_URL=$(az containerapp show \
    --name admin-webapp \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "📋 Service URLs:"
echo "🔐 Auth Service: https://$AUTH_SERVICE_URL"
echo "🌐 Admin Dashboard: https://$ADMIN_WEBAPP_URL"
echo ""
echo "🧪 Test URLs:"
echo "🔐 Auth Health: https://$AUTH_SERVICE_URL/health"
echo "🌐 Admin Dashboard: https://$ADMIN_WEBAPP_URL"
echo ""
echo "🚀 Your Admin Webapp and Auth Service are now live on Azure!"
