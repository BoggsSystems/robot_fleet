#!/bin/bash
# Azure Container Apps Deployment Script for Auth Service
# Prerequisites: Azure CLI installed and logged in

set -e

RESOURCE_GROUP="robot-fleet-simulator-rg"
CONTAINER_REGISTRY="robotfleetregistry"
CONTAINER_APP="warehouse-auth-service"
LOCATION="eastus"

echo "=== Azure Container Apps Deployment ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Container App: $CONTAINER_APP"
echo ""

# Check if logged in
echo "Checking Azure login..."
if ! az account show > /dev/null 2>&1; then
    echo "Not logged in. Running az login..."
    az login
fi

# Create resource group if it doesn't exist
echo "Creating resource group if needed..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# Create Container Registry if it doesn't exist
echo "Creating container registry if needed..."
az acr create --resource-group $RESOURCE_GROUP --name $CONTAINER_REGISTRY --sku Basic --output none

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --resource-group $RESOURCE_GROUP --name $CONTAINER_REGISTRY --query loginServer -o tsv)

# Log in to ACR
echo "Logging in to Container Registry..."
az acr login --name $CONTAINER_REGISTRY

# Build and push Docker image
echo "Building and pushing Docker image..."
docker build -t $ACR_LOGIN_SERVER/auth-service:latest .
docker push $ACR_LOGIN_SERVER/auth-service:latest

# Enable admin on ACR (for Container Apps)
az acr update -n $CONTAINER_REGISTRY --admin-enabled true

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --resource-group $RESOURCE_GROUP --name $CONTAINER_REGISTRY --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --resource-group $RESOURCE_GROUP --name $CONTAINER_REGISTRY --query passwords[0].value -o tsv)

# Create or update Container App
echo "Creating/updating Container App..."
az containerapp create \
    --name $CONTAINER_APP \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_LOGIN_SERVER/auth-service:latest \
    --target-port 3001 \
    --ingress external \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --environment-variables "ASPNETCORE_ENVIRONMENT=Production" \
    --min-replicas 1 \
    --max-replicas 3 \
    --cpu 0.5 \
    --memory 1Gi \
    --output table

# Get the app URL
APP_URL=$(az containerapp show --resource-group $RESOURCE_GROUP --name $CONTAINER_APP --query properties.configuration.ingress.fqdn -o tsv)

echo ""
echo "=== Deployment Complete ==="
echo "Auth Service URL: https://$APP_URL"
echo "Health Check: https://$APP_URL/health"
echo "Swagger UI: https://$APP_URL/swagger"
echo ""
