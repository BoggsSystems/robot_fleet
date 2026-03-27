#!/bin/bash

# Deploy Admin Dashboard to Azure Container App
echo "🚀 Deploying Admin Dashboard to Azure Container App"

# Configuration
RESOURCE_GROUP="robot-fleet-simulator-rg"
CONTAINER_APP_NAME="robot-fleet-admin"
LOCATION="eastus"
IMAGE_NAME="admin-dashboard"
REGISTRY="robotfleetregistry.azurecr.io"
IMAGE_TAG="latest"

# Build Docker image
echo "📦 Building Admin Dashboard Docker image..."
cd /Users/jeffboggs/robot_fleet/frontend/web/admin_dashboard

docker build --platform linux/amd64 -t ${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"

# Tag for Azure Container Registry
echo "🏷️  Tagging image for Azure Container Registry..."
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

# Push to Azure Container Registry
echo "📤 Pushing image to Azure Container Registry..."
docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

if [ $? -ne 0 ]; then
    echo "❌ Docker push failed"
    echo "Please ensure you're logged into Azure Container Registry:"
    echo "az acr login --name robotfleetregistry"
    exit 1
fi

echo "✅ Image pushed successfully to Azure Container Registry"

# Get ACR credentials for Container App
echo "🔑 Getting ACR credentials for Container App..."
ACR_USERNAME=$(az acr credential show --name robotfleetregistry --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name robotfleetregistry --query passwords[0].value --output tsv)

# Create or update Container App
echo "🔧 Creating/Updating Azure Container App..."

# Check if Container App exists
APP_EXISTS=$(az containerapp show --name ${CONTAINER_APP_NAME} --resource-group ${RESOURCE_GROUP} --query name --output tsv 2>/dev/null)

if [ ! -z "$APP_EXISTS" ]; then
    echo "🗑️  Deleting existing Container App..."
    az containerapp delete \
        --name ${CONTAINER_APP_NAME} \
        --resource-group ${RESOURCE_GROUP} \
        --yes
fi

echo "🆕 Creating new Container App..."
az containerapp create \
    --name ${CONTAINER_APP_NAME} \
    --resource-group ${RESOURCE_GROUP} \
    --image ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} \
    --environment robot-fleet-env \
    --ingress external \
    --target-port 80 \
    --min-replicas 1 \
    --max-replicas 2 \
    --cpu 0.5 \
    --memory 1Gi \
    --registry-server ${REGISTRY} \
    --registry-username ${ACR_USERNAME} \
    --registry-password ${ACR_PASSWORD} \
    --env-vars \
        NODE_ENV=production \
        REACT_APP_API_URL=https://robotfleet-ai.kindmoss-6eac8399.eastus.azurecontainerapps.io \
        REACT_APP_AUTH_URL=https://robotfleet-auth.kindmoss-6eac8399.eastus.azurecontainerapps.io

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

echo "🌐 Admin Dashboard is available at: https://${APP_URL}"

# Enable application insights for monitoring
echo "📊 Enabling Application Insights..."
az monitor app-insights component create \
    --app ${CONTAINER_APP_NAME}-insights \
    --location ${LOCATION} \
    --resource-group ${RESOURCE_GROUP} \
    --application-type web

# Connect Application Insights to Container App
INSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show \
    --app ${CONTAINER_APP_NAME}-insights \
    --resource-group ${RESOURCE_GROUP} \
    --query connectionString \
    --output tsv)

az containerapp update \
    --name ${CONTAINER_APP_NAME} \
    --resource-group ${RESOURCE_GROUP} \
    --env-vars \
        APPLICATIONINSIGHTS_CONNECTION_STRING=${INSIGHTS_CONNECTION_STRING}

echo "📈 Application Insights enabled for monitoring"

# Set up auto-scaling
echo "📈 Configuring auto-scaling..."
az containerapp update \
    --name ${CONTAINER_APP_NAME} \
    --resource-group ${RESOURCE_GROUP} \
    --scale-rule-name http-scaling \
    --scale-rule-type http \
    --scale-rule-metadata concurrentRequests=10 \
    --scale-rule-avg-concurrent-requests 10

echo "📊 Auto-scaling configured"

echo ""
echo "🎉 Admin Dashboard deployment completed!"
echo ""
echo "📋 Deployment Summary:"
echo "   - Container App: ${CONTAINER_APP_NAME}"
echo "   - Resource Group: ${RESOURCE_GROUP}"
echo "   - Location: ${LOCATION}"
echo "   - Image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
echo "   - URL: https://${APP_URL}"
echo "   - Replicas: 1-2 (auto-scaling)"
echo "   - Monitoring: Application Insights enabled"
echo ""
echo "🔗 Next Steps:"
echo "   1. Visit https://${APP_URL} to verify deployment"
echo "   2. Check Application Insights for monitoring data"
echo "   3. Configure custom domain if needed"
echo "   4. Set up SSL certificate for custom domain"
