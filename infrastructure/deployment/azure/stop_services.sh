#!/bin/bash

# Stop all Azure Container Apps to save costs by scaling to 0 replicas
echo "🛑 Stopping all Robot Fleet services..."

RESOURCE_GROUP="robot-fleet-simulator-rg"

echo "⏸️  Stopping Fleet Dashboard (scaling to 0 min replicas)..."
az containerapp update \
    --name robot-fleet-dashboard \
    --resource-group ${RESOURCE_GROUP} \
    --min-replicas 0

echo "⏸️  Stopping Admin Dashboard (scaling to 0 min replicas)..."
az containerapp update \
    --name robot-fleet-admin \
    --resource-group ${RESOURCE_GROUP} \
    --min-replicas 0

echo "⏸️  Stopping Auth Service (scaling to 0 min replicas)..."
az containerapp update \
    --name robotfleet-auth \
    --resource-group ${RESOURCE_GROUP} \
    --min-replicas 0

echo "⏸️  Stopping Event Processor (scaling to 0 min replicas)..."
az containerapp update \
    --name robot-fleet-event-processor \
    --resource-group ${RESOURCE_GROUP} \
    --min-replicas 0 2>/dev/null || echo "Event processor not found, skipping..."

echo "✅ All services stopped successfully!"
echo ""
echo "💰 Cost savings: All container apps scaled to 0 minimum replicas"
echo "📊 Current status: No running replicas (minimal cost)"
echo "🔗 To restart services, run: ./start_services.sh"
