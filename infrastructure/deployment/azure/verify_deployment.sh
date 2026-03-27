#!/bin/bash

# Verify Fleet Dashboard Deployment
echo "🔍 Verifying Fleet Dashboard deployment"

# Configuration
CONTAINER_APP_NAME="robot-fleet-dashboard"
RESOURCE_GROUP="robot-fleet-simulator-rg"

echo "📊 Getting Container App status..."
az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --output table

echo ""
echo "🌐 Getting Container App URL..."
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    --output tsv)

echo "URL: https://$APP_URL"

echo ""
echo "🏥 Checking application health..."
if curl -f -s "https://$APP_URL" > /dev/null; then
    echo "✅ Application is responding correctly"
else
    echo "❌ Application is not responding"
fi

echo ""
echo "📈 Getting replica information..."
az containerapp replica list \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --output table

echo ""
echo "📋 Getting recent logs..."
az containerapp logs show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --tail 20

echo ""
echo "🔍 Verification completed!"
echo "🌐 Fleet Dashboard: https://$APP_URL"
