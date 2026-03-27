#!/bin/bash

# Start all Azure Container Apps by scaling back to normal replicas
echo "🚀 Starting all Robot Fleet services..."

RESOURCE_GROUP="robot-fleet-simulator-rg"

echo "▶️  Starting Auth Service (scaling to 1-2 replicas)..."
az containerapp update \
    --name robotfleet-auth \
    --resource-group ${RESOURCE_GROUP} \
    --min-replicas 1 \
    --max-replicas 2

echo "▶️  Starting Admin Dashboard (scaling to 1-2 replicas)..."
az containerapp update \
    --name robot-fleet-admin \
    --resource-group ${RESOURCE_GROUP} \
    --min-replicas 1 \
    --max-replicas 2

echo "▶️  Starting Fleet Dashboard (scaling to 1-3 replicas)..."
az containerapp update \
    --name robot-fleet-dashboard \
    --resource-group ${RESOURCE_GROUP} \
    --min-replicas 1 \
    --max-replicas 3

echo "▶️  Starting Event Processor (scaling to 1-2 replicas)..."
az containerapp update \
    --name robot-fleet-event-processor \
    --resource-group ${RESOURCE_GROUP} \
    --min-replicas 1 \
    --max-replicas 2 2>/dev/null || echo "Event processor not found, skipping..."

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 30

echo ""
echo "🌐 Service URLs:"
echo "   Admin Dashboard: https://robot-fleet-admin.kindmoss-6eac8399.eastus.azurecontainerapps.io"
echo "   Fleet Dashboard: https://robot-fleet-dashboard.kindmoss-6eac8399.eastus.azurecontainerapps.io"
echo "   Auth Service:    https://robotfleet-auth.eastus.azurecontainerapps.io"

echo ""
echo "✅ All services started successfully!"
echo "💡 Tip: Wait 1-2 minutes for full initialization before testing"
echo "🔗 To stop services again, run: ./stop_services.sh"
