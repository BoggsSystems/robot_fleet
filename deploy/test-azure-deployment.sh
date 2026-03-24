#!/bin/bash

# Azure Deployment Testing Script
# Tests all services after deployment

set -e

echo "🧪 Starting Azure Deployment Tests"
echo "=================================="

# Variables
RESOURCE_GROUP="robot-fleet-simulator-rg"

# Get service URLs
echo "📋 Getting service URLs..."
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
echo "🌐 Service URLs:"
echo "🏭 Digital Twin: https://$DIGITAL_TWIN_URL"
echo "🧠 AI Engine: https://$AI_ENGINE_URL"
echo "🔄 Integration Hub: https://$INTEGRATION_HUB_URL"

echo ""
echo "📋 Step 1: Health Checks"

# Test Digital Twin Health
echo "🏭 Testing Digital Twin Service..."
if curl -f -s "https://$DIGITAL_TWIN_URL/health" > /dev/null; then
    echo "✅ Digital Twin Service: HEALTHY"
else
    echo "❌ Digital Twin Service: UNHEALTHY"
fi

# Test AI Engine Health
echo "🧠 Testing AI Engine..."
if curl -f -s "https://$AI_ENGINE_URL/health" > /dev/null; then
    echo "✅ AI Engine: HEALTHY"
else
    echo "❌ AI Engine: UNHEALTHY"
fi

# Test Integration Hub Health
echo "🔄 Testing Integration Hub..."
if curl -f -s "https://$INTEGRATION_HUB_URL/health" > /dev/null; then
    echo "✅ Integration Hub: HEALTHY"
else
    echo "❌ Integration Hub: UNHEALTHY"
fi

echo ""
echo "📋 Step 2: API Endpoint Tests"

# Test Digital Twin API
echo "🏭 Testing Digital Twin API..."
DIGITAL_TWIN_RESPONSE=$(curl -s -X POST "https://$DIGITAL_TWIN_URL/api/DigitalTwin/warehouse/configuration" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "test-client",
        "warehouseName": "Test Warehouse",
        "warehouseType": "Distribution",
        "totalArea": 50000,
        "zones": [
            {
                "name": "Test Zone",
                "zoneType": "Picking",
                "area": 10000,
                "capacity": 100
            }
        ],
        "robots": [
            {
                "name": "Test Robot",
                "robotType": "Humanoid",
                "batteryPct": 100.0
            }
        ]
    }')

if echo "$DIGITAL_TWIN_RESPONSE" | grep -q "warehouseId"; then
    echo "✅ Digital Twin API: WORKING"
    WAREHOUSE_ID=$(echo "$DIGITAL_TWIN_RESPONSE" | grep -o '"warehouseId":"[^"]*"' | cut -d'"' -f4)
    echo "   📦 Created Warehouse ID: $WAREHOUSE_ID"
else
    echo "❌ Digital Twin API: FAILED"
    echo "   Response: $DIGITAL_TWIN_RESPONSE"
fi

# Test AI Engine API
echo "🧠 Testing AI Engine API..."
AI_ENGINE_RESPONSE=$(curl -s -X POST "https://$AI_ENGINE_URL/api/ai/intent-parse" \
    -H "Content-Type: application/json" \
    -d '{
        "request_id": "test-001",
        "request_text": "Pick 5 items from zone B",
        "context": {"zone_type": "picking"}
    }')

if echo "$AI_ENGINE_RESPONSE" | grep -q "intent"; then
    echo "✅ AI Engine API: WORKING"
    PARSED_INTENT=$(echo "$AI_ENGINE_RESPONSE" | grep -o '"intent":"[^"]*"' | cut -d'"' -f4)
    echo "   🧠 Parsed Intent: $PARSED_INTENT"
else
    echo "❌ AI Engine API: FAILED"
    echo "   Response: $AI_ENGINE_RESPONSE"
fi

# Test Integration Hub API
echo "🔄 Testing Integration Hub API..."
HUB_RESPONSE=$(curl -s -X POST "https://$INTEGRATION_HUB_URL/api/communication/forward" \
    -H "Content-Type: application/json" \
    -d '{
        "target_service": "ai_engine",
        "endpoint": "/api/ai/intent-parse",
        "payload": {
            "request_id": "hub-test-001",
            "request_text": "Pick items from receiving zone"
        },
        "timeout": 30
    }')

if echo "$HUB_RESPONSE" | grep -q "status_code\|data"; then
    echo "✅ Integration Hub API: WORKING"
    echo "   🔄 Successfully forwarded request to AI Engine"
else
    echo "❌ Integration Hub API: FAILED"
    echo "   Response: $HUB_RESPONSE"
fi

echo ""
echo "📋 Step 3: Message Queue Tests"

# Test Message Queue
echo "📡 Testing Message Queue..."
QUEUE_RESPONSE=$(curl -s -X POST "https://$INTEGRATION_HUB_URL/api/messages/send" \
    -H "Content-Type: application/json" \
    -d '{
        "message_id": "test-msg-001",
        "source_service": "integration_hub",
        "target_service": "ai_engine",
        "message_type": "test_message",
        "payload": {"test": true, "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"},
        "priority": "medium",
        "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
    }')

if echo "$QUEUE_RESPONSE" | grep -q "sent\|queued"; then
    echo "✅ Message Queue: WORKING"
    MESSAGE_ID=$(echo "$QUEUE_RESPONSE" | grep -o '"message_id":"[^"]*"' | cut -d'"' -f4)
    echo "   📨 Message ID: $MESSAGE_ID"
    
    # Check message status
    sleep 2
    STATUS_RESPONSE=$(curl -s "https://$INTEGRATION_HUB_URL/api/messages/$MESSAGE_ID")
    if echo "$STATUS_RESPONSE" | grep -q "status"; then
        MESSAGE_STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        echo "   📊 Message Status: $MESSAGE_STATUS"
    fi
else
    echo "❌ Message Queue: FAILED"
    echo "   Response: $QUEUE_RESPONSE"
fi

echo ""
echo "📋 Step 4: Integration Tests"

# Test End-to-End Integration
echo "🔄 Testing End-to-End Integration..."
INTEGRATION_RESPONSE=$(curl -s -X POST "https://$INTEGRATION_HUB_URL/api/test/integration" \
    -H "Content-Type: application/json" \
    -d '{
        "test_config": {
            "connectivity_check": true,
            "message_flow_test": true,
            "synchronization_test": false,
            "performance_test": false
        }
    }')

if echo "$INTEGRATION_RESPONSE" | grep -q "overall_status"; then
    OVERALL_STATUS=$(echo "$INTEGRATION_RESPONSE" | grep -o '"overall_status":"[^"]*"' | cut -d'"' -f4)
    if [ "$OVERALL_STATUS" = "passed" ]; then
        echo "✅ Integration Tests: PASSED"
    else
        echo "⚠️ Integration Tests: $OVERALL_STATUS"
    fi
else
    echo "❌ Integration Tests: FAILED"
    echo "   Response: $INTEGRATION_RESPONSE"
fi

echo ""
echo "📋 Step 5: Performance Tests"

# Test Performance
echo "📊 Testing Performance..."
METRICS_RESPONSE=$(curl -s "https://$INTEGRATION_HUB_URL/api/metrics/services")

if echo "$METRICS_RESPONSE" | grep -q "services\|system"; then
    echo "✅ Metrics Collection: WORKING"
    
    # Extract some key metrics
    if echo "$METRICS_RESPONSE" | grep -q "healthy"; then
        HEALTHY_SERVICES=$(echo "$METRICS_RESPONSE" | grep -o '"healthy":[0-9]*' | cut -d':' -f2)
        echo "   💚 Healthy Services: $HEALTHY_SERVICES"
    fi
else
    echo "❌ Metrics Collection: FAILED"
fi

echo ""
echo "📋 Step 6: Circuit Breaker Tests"

# Test Circuit Breaker
echo "⚡ Testing Circuit Breaker..."
CIRCUIT_RESPONSE=$(curl -s "https://$INTEGRATION_HUB_URL/api/circuit-breaker/status")

if echo "$CIRCUIT_RESPONSE" | grep -q "digital_twin_service\|ai_engine"; then
    echo "✅ Circuit Breaker: WORKING"
    
    # Check circuit states
    if echo "$CIRCUIT_RESPONSE" | grep -q '"state":"closed"'; then
        echo "   🔓 Circuit Breaker State: CLOSED (Normal)"
    fi
else
    echo "❌ Circuit Breaker: FAILED"
fi

echo ""
echo "🎉 Testing Complete!"
echo "=================="

echo ""
echo "📋 Test Summary:"
echo "🌐 Service URLs:"
echo "   🏭 Digital Twin: https://$DIGITAL_TWIN_URL"
echo "   🧠 AI Engine: https://$AI_ENGINE_URL"
echo "   🔄 Integration Hub: https://$INTEGRATION_HUB_URL"
echo ""
echo "📚 API Documentation:"
echo "   🏭 Digital Twin API: https://$DIGITAL_TWIN_URL/swagger"
echo "   🧠 AI Engine API: https://$AI_ENGINE_URL/docs"
echo "   🔄 Integration Hub API: https://$INTEGRATION_HUB_URL/docs"
echo ""
echo "🔍 Monitoring:"
echo "   📊 Integration Hub Metrics: https://$INTEGRATION_HUB_URL/api/metrics/dashboard"
echo "   📊 Service Health: https://$INTEGRATION_HUB_URL/health"
echo ""
echo "🧪 Manual Testing Commands:"
echo "   # Test intent parsing:"
echo "   curl -X POST https://$AI_ENGINE_URL/api/ai/intent-parse -H 'Content-Type: application/json' -d '{\"request_id\":\"test\",\"request_text\":\"Pick items from zone A\"}'"
echo ""
echo "   # Create warehouse configuration:"
echo "   curl -X POST https://$DIGITAL_TWIN_URL/api/DigitalTwin/warehouse/configuration -H 'Content-Type: application/json' -d '{\"clientId\":\"test\",\"warehouseName\":\"Test Warehouse\",\"warehouseType\":\"Distribution\",\"totalArea\":50000}'"
echo ""
echo "   # Check system health:"
echo "   curl https://$INTEGRATION_HUB_URL/health"
echo ""
echo "🚀 Your Warehouse AI System is ready for use!"
