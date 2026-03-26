#!/bin/bash

# Azure Deployment Script for Warehouse AI System
# Uses existing robot-fleet-simulator-rg infrastructure

set -e

echo "🚀 Starting Azure Deployment for Warehouse AI System"
echo "📍 Using existing resource group: robot-fleet-simulator-rg"
echo "📍 Using existing environment: robot-fleet-env"

# Variables
RESOURCE_GROUP="robot-fleet-simulator-rg"
LOCATION="eastus"
ENVIRONMENT="robot-fleet-env"
REGISTRY="robotfleetregistry"

echo ""
echo "📋 Step 1: Creating missing Azure services..."

# Create Service Bus (only if it doesn't exist)
echo "🔍 Checking Service Bus namespace..."
if ! az servicebus namespace show --name warehouse-ai-servicebus --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "📡 Creating Service Bus namespace..."
    az servicebus namespace create \
        --name warehouse-ai-servicebus \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Standard
else
    echo "✅ Service Bus namespace already exists"
fi

# Create Service Bus queues
echo "📤 Creating Service Bus queues..."
az servicebus queue create \
    --namespace-name warehouse-ai-servicebus \
    --name warehouse-digital-twin-service \
    --resource-group $RESOURCE_GROUP || echo "Queue already exists"

az servicebus queue create \
    --namespace-name warehouse-ai-servicebus \
    --name warehouse-ai-engine \
    --resource-group $RESOURCE_GROUP || echo "Queue already exists"

az servicebus queue create \
    --namespace-name warehouse-ai-servicebus \
    --name warehouse-integration-hub \
    --resource-group $RESOURCE_GROUP || echo "Queue already exists"

# Create Application Insights (only if it doesn't exist)
echo "🔍 Checking Application Insights..."
if ! az monitor app-insights component show --app warehouse-insights --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "📊 Creating Application Insights..."
    az monitor app-insights component create \
        --app warehouse-insights \
        --location $LOCATION \
        --resource-group $RESOURCE_GROUP \
        --application-type web
else
    echo "✅ Application Insights already exists"
fi

echo ""
echo "📋 Step 2: Getting connection strings and endpoints..."

# Get Service Bus connection string
SERVICE_BUS_CONNECTION=$(az servicebus namespace authorization-rule keys list \
    --namespace-name warehouse-ai-servicebus \
    --resource-group $RESOURCE_GROUP \
    --name RootManageSharedAccessKey \
    --query primaryConnectionString \
    --output tsv)

# Get Cosmos DB endpoint and key
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

# Get Digital Twins endpoint
DIGITAL_TWINS_ENDPOINT=$(az dt show \
    --dt-name robot-fleet-digital-twins \
    --resource-group $RESOURCE_GROUP \
    --query hostname \
    --output tsv)

# Get Application Insights key
APP_INSIGHTS_KEY=$(az monitor app-insights component show \
    --app warehouse-insights \
    --resource-group $RESOURCE_GROUP \
    --query instrumentationKey \
    --output tsv)

echo ""
echo "📋 Step 3: Building container images..."

# Build C# Digital Twin Service
echo "🏗️ Building C# Digital Twin Service..."
cd backend/services/digital_twin_management
docker build -t $REGISTRY/warehouse-digital-twin:latest .
docker push $REGISTRY/warehouse-digital-twin:latest

# Build Python AI Engine
echo "🧠 Building Python AI Engine..."
cd ../ai_engine
docker build -t $REGISTRY/warehouse-ai-engine:latest .
docker push $REGISTRY/warehouse-ai-engine:latest

# Build Integration Hub
echo "🔄 Building Integration Hub..."
cd ../integration_hub
docker build -t $REGISTRY/warehouse-integration-hub:latest .
docker push $REGISTRY/warehouse-integration-hub:latest

# Build Auth Service
echo "🔐 Building Auth Service..."
cd ../auth_csharp
docker build -t $REGISTRY/warehouse-auth-service:latest .
docker push $REGISTRY/warehouse-auth-service:latest

cd ../../../

echo ""
echo "📋 Step 4: Building Admin Web Dashboard..."

# Build Admin Web Dashboard
echo "🌐 Building Admin Web Dashboard..."
cd frontend/web/admin_dashboard

# Get auth service URL for build
AUTH_URL=$(az containerapp show \
    --name warehouse-auth-service \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv 2>/dev/null || echo "warehouse-auth-service.kindmoss-6eac8399.eastus.azurecontainerapps.net")

docker build \
    --build-arg REACT_APP_AUTH_URL=https://$AUTH_URL \
    -t $REGISTRY/admin-webapp:latest .
docker push $REGISTRY/admin-webapp:latest

cd ../../../

echo ""
echo "📋 Step 5: Deploying services to Container Apps..."

# Deploy C# Digital Twin Service
echo "🏭 Deploying C# Digital Twin Service..."
az containerapp create \
    --name warehouse-digital-twin \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image $REGISTRY/warehouse-digital-twin:latest \
    --cpu 1 \
    --memory 2Gi \
    --env-vars \
        AzureDigitalTwins__Endpoint="https://$DIGITAL_TWINS_ENDPOINT" \
        ApplicationInsights__InstrumentationKey="$APP_INSIGHTS_KEY" \
        COSMOS_DB__Endpoint="$COSMOS_ENDPOINT" \
        COSMOS_DB__Key="$COSMOS_KEY" \
    --ingress external \
    --target-port 80

# Deploy Python AI Engine
echo "🧠 Deploying Python AI Engine..."
az containerapp create \
    --name warehouse-ai-engine \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image $REGISTRY/warehouse-ai-engine:latest \
    --cpu 2 \
    --memory 4Gi \
    --env-vars \
        LOG_LEVEL="INFO" \
        OPENAI_API_KEY="" \
        AZURE_COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
        AZURE_SERVICE_BUS_CONNECTION="$SERVICE_BUS_CONNECTION" \
    --ingress external \
    --target-port 8000

# Deploy Integration Hub
echo "🔄 Deploying Integration Hub..."
az containerapp create \
    --name warehouse-integration-hub \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT \
    --image $REGISTRY/warehouse-integration-hub:latest \
    --cpu 1.5 \
    --memory 3Gi \
    --env-vars \
        AZURE_SERVICE_BUS_CONNECTION="$SERVICE_BUS_CONNECTION" \
        AZURE_COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
        AZURE_COSMOS_KEY="$COSMOS_KEY" \
        LOG_LEVEL="INFO" \
        C#_SERVICE_URL="https://warehouse-digital-twin.kindmoss-6eac8399.eastus.azurecontainerapps.io" \
    --ingress external \
    --target-port 9000

# Deploy Auth Service
echo "🔐 Deploying Auth Service..."
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

# Deploy Admin Web Dashboard
echo "🌐 Deploying Admin Web Dashboard..."
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

ADMIN_WEBAPP_URL=$(az containerapp show \
    --name admin-webapp \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

AUTH_SERVICE_URL=$(az containerapp show \
    --name warehouse-auth-service \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "📋 Service URLs:"
echo "🏭 C# Digital Twin Service: https://$DIGITAL_TWIN_URL"
echo "🧠 Python AI Engine: https://$AI_ENGINE_URL"
echo "🔄 Integration Hub: https://$INTEGRATION_HUB_URL"
echo "🔐 Auth Service: https://$AUTH_SERVICE_URL"
echo "🌐 Admin Dashboard: https://$ADMIN_WEBAPP_URL"
echo ""
echo "📋 Health Check URLs:"
echo "🏭 Digital Twin Health: https://$DIGITAL_TWIN_URL/health"
echo "🧠 AI Engine Health: https://$AI_ENGINE_URL/health"
echo "🔄 Integration Hub Health: https://$INTEGRATION_HUB_URL/health"
echo ""
echo "📋 API Documentation:"
echo "🏭 Digital Twin API: https://$DIGITAL_TWIN_URL/swagger"
echo "🧠 AI Engine API: https://$AI_ENGINE_URL/docs"
echo "🔄 Integration Hub API: https://$INTEGRATION_HUB_URL/docs"
echo ""
echo "🔑 Connection Strings (save these for configuration):"
echo "📡 Service Bus Connection: $SERVICE_BUS_CONNECTION"
echo "🗄️ Cosmos DB Endpoint: $COSMOS_ENDPOINT"
echo "🔑 Cosmos DB Key: $COSMOS_KEY"
echo "🏭 Digital Twins Endpoint: https://$DIGITAL_TWINS_ENDPOINT"
echo "📊 App Insights Key: $APP_INSIGHTS_KEY"
echo ""
echo "🧪 Next Steps:"
echo "1. Test health checks: curl https://$INTEGRATION_HUB_URL/health"
echo "2. Test API endpoints: curl https://$AI_ENGINE_URL/api/ai/intent-parse"
echo "3. Check Azure Portal for monitoring"
echo "4. Run integration tests"
echo ""
echo "🚀 Your Warehouse AI System is now live on Azure!"
