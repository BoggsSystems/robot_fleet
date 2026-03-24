# 🚀 Azure Deployment Guide

## 📋 Overview

This guide walks through deploying the complete C# + Python Warehouse AI system to Azure using your existing infrastructure.

## 🏗️ Architecture

```
☁️ Azure Resources (robot-fleet-simulator-rg):
├── 🏭 C# Digital Twin Service → Container App
├── 🧠 Python AI Engine → Container App  
├── 🔄 Integration Hub → Container App
├── 📡 Azure Service Bus → Message Queues (NEW)
├── 🗄️ Azure Cosmos DB → Data Storage (EXISTING)
├── 🏭 Azure Digital Twins → Warehouse Models (EXISTING)
├── 📊 Application Insights → Monitoring (NEW)
├── 🌐 Container Apps Environment (EXISTING)
└── 🐳 Container Registry (EXISTING)
```

## 🎯 Prerequisites

### **Azure CLI**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"
```

### **Docker**
```bash
# Install Docker (if not already installed)
# For Ubuntu/Debian:
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### **Verify Existing Resources**
```bash
# Check your existing resource groups
az group list --output table

# Verify Container Apps environment
az containerapp env show --name robot-fleet-env --resource-group robot-fleet-simulator-rg

# Verify Cosmos DB
az cosmosdb show --name robot-fleet-cosmos --resource-group robot-fleet-simulator-rg

# Verify Digital Twins
az dt show --dt-name robot-fleet-digital-twins --resource-group robot-fleet-simulator-rg
```

## 🚀 Quick Deployment

### **Step 1: Make Scripts Executable**
```bash
chmod +x deploy/azure-setup.sh
chmod +x deploy/test-azure-deployment.sh
```

### **Step 2: Run Deployment**
```bash
# Execute the deployment script
./deploy/azure-setup.sh
```

### **Step 3: Test Deployment**
```bash
# Run comprehensive tests
./deploy/test-azure-deployment.sh
```

## 📋 Manual Deployment Steps

If you prefer to run commands manually:

### **1. Create Missing Services**
```bash
# Create Service Bus namespace
az servicebus namespace create \
    --name warehouse-servicebus \
    --resource-group robot-fleet-simulator-rg \
    --location eastus \
    --sku Standard

# Create Service Bus queues
az servicebus queue create \
    --namespace-name warehouse-servicebus \
    --name warehouse-digital-twin-service \
    --resource-group robot-fleet-simulator-rg

az servicebus queue create \
    --namespace-name warehouse-servicebus \
    --name warehouse-ai-engine \
    --resource-group robot-fleet-simulator-rg

# Create Application Insights
az monitor app-insights component create \
    --app warehouse-insights \
    --location eastus \
    --resource-group robot-fleet-simulator-rg \
    --application-type web
```

### **2. Build Container Images**
```bash
# Build C# Digital Twin Service
cd services/digital_twin_management
docker build -f ../deploy/dockerfiles/Dockerfile.digital-twin -t robotfleetregistry/warehouse-digital-twin:latest .
docker push robotfleetregistry/warehouse-digital-twin:latest

# Build Python AI Engine
cd ../ai_engine
docker build -f ../deploy/dockerfiles/Dockerfile.ai-engine -t robotfleetregistry/warehouse-ai-engine:latest .
docker push robotfleetregistry/warehouse-ai-engine:latest

# Build Integration Hub
cd ../integration_hub
docker build -f ../deploy/dockerfiles/Dockerfile.integration-hub -t robotfleetregistry/warehouse-integration-hub:latest .
docker push robotfleetregistry/warehouse-integration-hub:latest

cd ../../
```

### **3. Deploy Services**
```bash
# Get connection strings
SERVICE_BUS_CONNECTION=$(az servicebus namespace authorization-rule keys list \
    --namespace-name warehouse-servicebus \
    --resource-group robot-fleet-simulator-rg \
    --name RootManageSharedAccessKey \
    --query primaryConnectionString \
    --output tsv)

COSMOS_ENDPOINT=$(az cosmosdb show \
    --name robot-fleet-cosmos \
    --resource-group robot-fleet-simulator-rg \
    --query documentEndpoint \
    --output tsv)

COSMOS_KEY=$(az cosmosdb keys list \
    --name robot-fleet-cosmos \
    --resource-group robot-fleet-simulator-rg \
    --query primaryMasterKey \
    --output tsv)

DIGITAL_TWINS_ENDPOINT=$(az dt show \
    --dt-name robot-fleet-digital-twins \
    --resource-group robot-fleet-simulator-rg \
    --query hostname \
    --output tsv)

APP_INSIGHTS_KEY=$(az monitor app-insights component show \
    --app warehouse-insights \
    --resource-group robot-fleet-simulator-rg \
    --query instrumentationKey \
    --output tsv)

# Deploy C# Digital Twin Service
az containerapp create \
    --name warehouse-digital-twin \
    --resource-group robot-fleet-simulator-rg \
    --environment robot-fleet-env \
    --image robotfleetregistry/warehouse-digital-twin:latest \
    --cpu 1 \
    --memory 2Gi \
    --env-vars \
        AzureDigitalTwins__Endpoint="https://$DIGITAL_TWINS_ENDPOINT" \
        ApplicationInsights__InstrumentationKey="$APP_INSIGHTS_KEY" \
    --ingress external \
    --target-port 80

# Deploy Python AI Engine
az containerapp create \
    --name warehouse-ai-engine \
    --resource-group robot-fleet-simulator-rg \
    --environment robot-fleet-env \
    --image robotfleetregistry/warehouse-ai-engine:latest \
    --cpu 2 \
    --memory 4Gi \
    --env-vars \
        LOG_LEVEL="INFO" \
        AZURE_SERVICE_BUS_CONNECTION="$SERVICE_BUS_CONNECTION" \
    --ingress external \
    --target-port 8000

# Deploy Integration Hub
az containerapp create \
    --name warehouse-integration-hub \
    --resource-group robot-fleet-simulator-rg \
    --environment robot-fleet-env \
    --image robotfleetregistry/warehouse-integration-hub:latest \
    --cpu 1.5 \
    --memory 3Gi \
    --env-vars \
        AZURE_SERVICE_BUS_CONNECTION="$SERVICE_BUS_CONNECTION" \
        AZURE_COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
        AZURE_COSMOS_KEY="$COSMOS_KEY" \
    --ingress external \
    --target-port 9000
```

## 🧪 Testing the Deployment

### **Health Checks**
```bash
# Get service URLs
DIGITAL_TWIN_URL=$(az containerapp show \
    --name warehouse-digital-twin \
    --resource-group robot-fleet-simulator-rg \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

AI_ENGINE_URL=$(az containerapp show \
    --name warehouse-ai-engine \
    --resource-group robot-fleet-simulator-rg \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

INTEGRATION_HUB_URL=$(az containerapp show \
    --name warehouse-integration-hub \
    --resource-group robot-fleet-simulator-rg \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

# Test health endpoints
curl https://$DIGITAL_TWIN_URL/health
curl https://$AI_ENGINE_URL/health
curl https://$INTEGRATION_HUB_URL/health
```

### **API Tests**
```bash
# Test Digital Twin API
curl -X POST https://$DIGITAL_TWIN_URL/api/DigitalTwin/warehouse/configuration \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "test-client",
        "warehouseName": "Test Warehouse",
        "warehouseType": "Distribution",
        "totalArea": 50000
    }'

# Test AI Engine API
curl -X POST https://$AI_ENGINE_URL/api/ai/intent-parse \
    -H "Content-Type: application/json" \
    -d '{
        "request_id": "test-001",
        "request_text": "Pick 5 items from zone B",
        "context": {"zone_type": "picking"}
    }'

# Test Integration Hub
curl -X POST https://$INTEGRATION_HUB_URL/api/communication/forward \
    -H "Content-Type: application/json" \
    -d '{
        "target_service": "ai_engine",
        "endpoint": "/api/ai/intent-parse",
        "payload": {
            "request_id": "hub-test",
            "request_text": "Pick items from receiving zone"
        }
    }'
```

### **End-to-End Test**
```bash
# 1. Create warehouse configuration
WAREHOUSE_RESPONSE=$(curl -X POST https://$DIGITAL_TWIN_URL/api/DigitalTwin/warehouse/configuration \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "test-client",
        "warehouseName": "Azure Test Warehouse",
        "warehouseType": "Distribution",
        "totalArea": 75000,
        "zones": [
            {
                "name": "Receiving Zone",
                "zoneType": "Receiving",
                "area": 15000,
                "capacity": 150
            }
        ],
        "robots": [
            {
                "name": "Picker-001",
                "robotType": "Humanoid",
                "batteryPct": 95.0
            }
        ]
    }')

# 2. Generate mission plan
curl -X POST https://$AI_ENGINE_URL/api/ai/mission-plan \
    -H "Content-Type: application/json" \
    -d '{
        "request_id": "mission-001",
        "request_text": "Pick 10 items from receiving zone and move to packing",
        "priority": "high",
        "current_state": {
            "available_robots": 1,
            "zone_occupancy": {"receiving": 25}
        }
    }'

# 3. Test data synchronization
curl -X POST https://$INTEGRATION_HUB_URL/api/synchronization/sync \
    -H "Content-Type: application/json" \
    -d '{
        "sync_type": "unidirectional",
        "source_data": {
            "warehouse_id": "test-warehouse",
            "robot_status": {"robot-001": "busy"}
        },
        "target_service": "digital_twin_service",
        "sync_options": {
            "entity_type": "robot_status",
            "conflict_resolution": "last_write_wins"
        }
    }'
```

## 🔧 Configuration

### **Environment Variables**
```bash
# C# Digital Twin Service
AzureDigitalTwins__Endpoint=https://robot-fleet-digital-twins.api.eastus.digitaltwins.azure.net
ApplicationInsights__InstrumentationKey=your-app-insights-key

# Python AI Engine
LOG_LEVEL=INFO
AZURE_SERVICE_BUS_CONNECTION=your-service-bus-connection
OPENAI_API_KEY=your-openai-api-key (optional)

# Integration Hub
AZURE_SERVICE_BUS_CONNECTION=your-service-bus-connection
AZURE_COSMOS_ENDPOINT=https://robot-fleet-cosmos.documents.azure.com:443/
AZURE_COSMOS_KEY=your-cosmos-key
LOG_LEVEL=INFO
```

### **Service URLs**
After deployment, your services will be available at:
- **Digital Twin Service**: `https://warehouse-digital-twin.<unique-hash>.eastus.azurecontainerapps.io`
- **AI Engine**: `https://warehouse-ai-engine.<unique-hash>.eastus.azurecontainerapps.io`
- **Integration Hub**: `https://warehouse-integration-hub.<unique-hash>.eastus.azurecontainerapps.io`

## 📊 Monitoring

### **Azure Portal Monitoring**
1. **Container Apps**: Check logs, metrics, and health status
2. **Service Bus**: Monitor queue depth and message throughput
3. **Cosmos DB**: Check request units and storage usage
4. **Application Insights**: Review performance and error tracking

### **API Monitoring**
```bash
# Get comprehensive health
curl https://warehouse-integration-hub.<hash>.azurecontainerapps.io/health

# Get service metrics
curl https://warehouse-integration-hub.<hash>.azurecontainerapps.io/api/metrics/services

# Get dashboard data
curl https://warehouse-integration-hub.<hash>.azurecontainerapps.io/api/metrics/dashboard
```

## 🔍 Troubleshooting

### **Common Issues**

#### **Service Not Starting**
```bash
# Check container app logs
az containerapp logs show --name warehouse-digital-twin --resource-group robot-fleet-simulator-rg

# Check revision
az containerapp revision show --name warehouse-digital-twin --resource-group robot-fleet-simulator-rg
```

#### **Connection Issues**
```bash
# Check Service Bus connection
az servicebus namespace show --name warehouse-servicebus --resource-group robot-fleet-simulator-rg

# Check Cosmos DB connection
az cosmosdb show --name robot-fleet-cosmos --resource-group robot-fleet-simulator-rg
```

#### **Performance Issues**
```bash
# Scale up resources
az containerapp update \
    --name warehouse-ai-engine \
    --resource-group robot-fleet-simulator-rg \
    --cpu 4 \
    --memory 8Gi
```

### **Debugging Commands**
```bash
# Get service status
az containerapp show --name warehouse-digital-twin --resource-group robot-fleet-simulator-rg

# Get environment variables
az containerapp env show --name robot-fleet-env --resource-group robot-fleet-simulator-rg

# Check networking
az containerapp ingress show --name warehouse-digital-twin --resource-group robot-fleet-simulator-rg
```

## 🧹 Cleanup

### **Remove Services (if needed)**
```bash
# Delete container apps
az containerapp delete --name warehouse-digital-twin --resource-group robot-fleet-simulator-rg
az containerapp delete --name warehouse-ai-engine --resource-group robot-fleet-simulator-rg
az containerapp delete --name warehouse-integration-hub --resource-group robot-fleet-simulator-rg

# Delete Service Bus (optional)
az servicebus namespace delete --name warehouse-servicebus --resource-group robot-fleet-simulator-rg

# Delete Application Insights (optional)
az monitor app-insights component delete --app warehouse-insights --resource-group robot-fleet-simulator-rg
```

## 📚 Next Steps

1. **Configure OpenAI API** (if using advanced AI features)
2. **Set up monitoring alerts** in Azure Monitor
3. **Configure auto-scaling** for production workloads
4. **Set up CI/CD pipeline** for automated deployments
5. **Implement backup and disaster recovery**

## 🎉 Success!

Your Warehouse AI System is now running on Azure! You have:
- ✅ C# Digital Twin Service with Azure Digital Twins integration
- ✅ Python AI Engine with intent understanding and optimization
- ✅ Integration Hub with message queues and monitoring
- ✅ Complete observability and fault tolerance

The system is ready for production use and can handle real warehouse operations with AI-powered optimization!
