#!/bin/bash

# Setup Azure for Fleet Dashboard Deployment
echo "🔧 Setting up Azure for Fleet Dashboard deployment"

# Configuration
RESOURCE_GROUP="robot-fleet-simulator-rg"
LOCATION="eastus"
ACR_NAME="kindmoss-6eac8399"
CONTAINER_APP_ENV="robot-fleet-env"

echo "🔐 Logging into Azure..."
# Login to Azure (interactive)
az login

echo "📋 Setting subscription..."
# Set subscription (you may need to choose the right one)
az account show --output table
echo "Enter the subscription ID to use (or press Enter to use current):"
read SUBSCRIPTION_ID
if [ ! -z "$SUBSCRIPTION_ID" ]; then
    az account set --subscription $SUBSCRIPTION_ID
fi

echo "🏗️  Creating resource group (if not exists)..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

echo "📦 Creating Container Registry (if not exists)..."
az acr create \
    --name robotfleetregistry \
    --resource-group $RESOURCE_GROUP \
    --sku Basic \
    --admin-enabled true \
    --output none

echo "🌐 Creating Container App Environment (if not exists)..."
az containerapp env create \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output none

echo "🔑 Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name robotfleetregistry --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name robotfleetregistry --query passwords[0].value --output tsv)

echo "🔐 Logging into Docker..."
echo "$ACR_PASSWORD" | docker login robotfleetregistry.azurecr.io --username $ACR_USERNAME --password-stdin

echo "📝 Saving credentials to .env file..."
cat > .env << EOF
ACR_NAME=robotfleetregistry
ACR_USERNAME=$ACR_USERNAME
ACR_PASSWORD=$ACR_PASSWORD
RESOURCE_GROUP=$RESOURCE_GROUP
LOCATION=$LOCATION
CONTAINER_APP_ENV=$CONTAINER_APP_ENV
EOF

echo "✅ Azure setup completed!"
echo ""
echo "📋 Configuration saved to .env file"
echo "🔐 You are now logged into Azure Container Registry"
echo "🚀 You can now run: ./deploy_fleet_dashboard_azure.sh"
echo ""
echo "📋 Useful Commands:"
echo "   - View resource groups: az group list"
echo "   - View ACR repositories: az acr repository list --name robotfleetregistry"
echo "   - View Container Apps: az containerapp list --resource-group $RESOURCE_GROUP"
