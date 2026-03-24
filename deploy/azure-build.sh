#!/bin/bash

# Azure Container Registry Build Script
# Builds containers in Azure cloud without local Docker

set -e

echo "🚀 Building containers in Azure Cloud..."

# Variables
RESOURCE_GROUP="robot-fleet-simulator-rg"
REGISTRY="robotfleetregistry"
LOCATION="eastus"

echo ""
echo "📋 Step 1: Building C# Digital Twin Service..."

# Build C# service in Azure
az acr build \
    --registry $REGISTRY \
    --image warehouse-digital-twin:latest \
    --resource-group $RESOURCE_GROUP \
    services/digital_twin_management/ \
    --platform linux/amd64

echo ""
echo "📋 Step 2: Building Python AI Engine..."

# Build Python AI Engine in Azure
az acr build \
    --registry $REGISTRY \
    --image warehouse-ai-engine:latest \
    --resource-group $RESOURCE_GROUP \
    services/ai_engine/ \
    --platform linux/amd64

echo ""
echo "📋 Step 3: Building Integration Hub..."

# Build Integration Hub in Azure
az acr build \
    --registry $REGISTRY \
    --image warehouse-integration-hub:latest \
    --resource-group $RESOURCE_GROUP \
    services/integration_hub/ \
    --platform linux/amd64

echo ""
echo "✅ All images built successfully in Azure!"
echo ""
echo "📋 Step 4: Deploying to Container Apps..."

# Get connection strings
SERVICE_BUS_CONNECTION=$(az servicebus namespace authorization-rule keys list \
    --namespace-name warehouse-ai-servicebus \
    --resource-group $RESOURCE_GROUP \
    --name RootManageSharedAccessKey \
    --query primaryConnectionString \
    --output tsv)

COSMOS_ENDPOINT=$(az cosmosdb show \
    --name robot-fleet-cosmos \
    --resource-group $RESOURCE_GROUP \
    --query documentEndpoint \
    --output tsv)

COSMOS_KEY=$(az cosmosdb keys list \
    --name robot-fleet-cosmos \
    --resource-group $RESOURCE_GROUP \
    --query primaryMasterKey \
    --output tsv)

DIGITAL_TWINS_ENDPOINT=$(az dt show \
    --dt-name robot-fleet-digital-twins \
    --resource-group $RESOURCE_GROUP \
    --query hostname \
    --output tsv)

APP_INSIGHTS_KEY=$(az monitor app-insights component show \
    --app warehouse-insights \
    --resource-group $RESOURCE_GROUP \
    --query instrumentationKey \
    --output tsv)

# Deploy C# Digital Twin Service
echo "🏭 Deploying C# Digital Twin Service..."
az containerapp create \
    --name warehouse-digital-twin \
    --resource-group $RESOURCE_GROUP \
    --environment robot-fleet-env \
    --image $REGISTRY/warehouse-digital-twin:latest \
    --cpu 1 \
    --memory 2Gi \
    --env-vars \
        AzureDigitalTwins__Endpoint="https://$DIGITAL_TWINS_ENDPOINT" \
        ApplicationInsights__InstrumentationKey="$APP_INSIGHTS_KEY" \
    --ingress external \
    --target-port 80

# Deploy Python AI Engine
echo "🧠 Deploying Python AI Engine..."
az containerapp create \
    --name warehouse-ai-engine \
    --resource-group $RESOURCE_GROUP \
    --environment robot-fleet-env \
    --image $REGISTRY/warehouse-ai-engine:latest \
    --cpu 2 \
    --memory 4Gi \
    --env-vars \
        LOG_LEVEL="INFO" \
        AZURE_SERVICE_BUS_CONNECTION="$SERVICE_BUS_CONNECTION" \
    --ingress external \
    --target-port 8000

# Deploy Integration Hub
echo "🔄 Deploying Integration Hub..."
az containerapp create \
    --name warehouse-integration-hub \
    --resource-group $RESOURCE_GROUP \
    --environment robot-fleet-env \
    --image $REGISTRY/warehouse-integration-hub:latest \
    --cpu 1.5 \
    --memory 3Gi \
    --env-vars \
        AZURE_SERVICE_BUS_CONNECTION="$SERVICE_BUS_CONNECTION" \
        AZURE_COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
        AZURE_COSMOS_KEY="$COSMOS_KEY" \
    --ingress external \
    --target-port 9000

echo ""
echo "🎉 Deployment Complete!"

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
echo "🏭 C# Digital Twin Service: https://$DIGITAL_TWIN_URL"
echo "🧠 Python AI Engine: https://$AI_ENGINE_URL"
echo "🔄 Integration Hub: https://$INTEGRATION_HUB_URL"
