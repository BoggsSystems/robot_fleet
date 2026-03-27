#!/bin/bash

# Deploy Fleet Dashboard to Azure using Bicep
echo "🚀 Deploying Fleet Dashboard to Azure using Bicep"

# Configuration
RESOURCE_GROUP="robot-fleet-simulator-rg"
LOCATION="eastus"
ACR_NAME="kindmoss-6eac8399"
IMAGE_TAG="latest"
DEPLOYMENT_NAME="fleet-dashboard-deployment"

# Build and push Docker image
echo "📦 Building and pushing Fleet Dashboard image..."
cd /Users/jeffboggs/robot_fleet/frontend/web/fleet_dashboard

# Build the image
docker build -t fleet-dashboard:${IMAGE_TAG} .

# Tag for ACR
docker tag fleet-dashboard:${IMAGE_TAG} ${ACR_NAME}.azurecr.io/fleet-dashboard:${IMAGE_TAG}

# Push to ACR
echo "📤 Pushing to Azure Container Registry..."
docker push ${ACR_NAME}.azurecr.io/fleet-dashboard:${IMAGE_TAG}

if [ $? -ne 0 ]; then
    echo "❌ Failed to push to ACR. Please ensure you're logged in:"
    echo "az acr login --name ${ACR_NAME}"
    exit 1
fi

echo "✅ Image pushed successfully"

# Get ACR credentials
echo "🔑 Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name ${ACR_NAME} --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name ${ACR_NAME} --query passwords[0].value --output tsv)

# Deploy using Bicep
echo "🏗️  Deploying infrastructure with Bicep..."
az deployment group create \
    --resource-group ${RESOURCE_GROUP} \
    --name ${DEPLOYMENT_NAME} \
    --template-file fleet-dashboard.bicep \
    --parameters \
        location=${LOCATION} \
        acrUsername=${ACR_USERNAME} \
        acrPassword=${ACR_PASSWORD} \
        imageTag=${IMAGE_TAG}

if [ $? -ne 0 ]; then
    echo "❌ Bicep deployment failed"
    exit 1
fi

echo "✅ Bicep deployment completed successfully"

# Get the deployed app URL
echo "🔍 Getting deployment details..."
APP_URL=$(az deployment group show \
    --resource-group ${RESOURCE_GROUP} \
    --name ${DEPLOYMENT_NAME} \
    --query properties.outputs.containerAppUrl.value \
    --output tsv)

APP_INSIGHTS_KEY=$(az deployment group show \
    --resource-group ${RESOURCE_GROUP} \
    --name ${DEPLOYMENT_NAME} \
    --query properties.outputs.appInsightsInstrumentationKey.value \
    --output tsv)

echo ""
echo "🎉 Fleet Dashboard deployment completed!"
echo ""
echo "📋 Deployment Summary:"
echo "   - Resource Group: ${RESOURCE_GROUP}"
echo "   - Location: ${LOCATION}"
echo "   - Container Registry: ${ACR_NAME}.azurecr.io"
echo "   - Image: ${ACR_NAME}.azurecr.io/fleet-dashboard:${IMAGE_TAG}"
echo "   - URL: https://${APP_URL}"
echo "   - App Insights Key: ${APP_INSIGHTS_KEY}"
echo ""
echo "🔗 Next Steps:"
echo "   1. Visit https://${APP_URL} to verify the deployment"
echo "   2. Monitor performance in Azure Portal (Application Insights)"
echo "   3. Configure custom domain if needed"
echo "   4. Set up CDN for better performance"
echo ""
echo "🔧 Management Commands:"
echo "   - View logs: az containerapp logs show --name robot-fleet-dashboard --resource-group ${RESOURCE_GROUP}"
echo "   - Scale: az containerapp update --name robot-fleet-dashboard --resource-group ${RESOURCE_GROUP} --min-replicas 1 --max-replicas 5"
echo "   - Update: az containerapp update --name robot-fleet-dashboard --resource-group ${RESOURCE_GROUP} --image ${ACR_NAME}.azurecr.io/fleet-dashboard:new-tag"
