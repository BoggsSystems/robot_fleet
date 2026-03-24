# Event Processor Service

IoT Hub event processing service for robot fleet telemetry, Digital Twins synchronization, and alert management.

## Features

- **Real-time Telemetry Processing**: Ingest robot telemetry from Azure IoT Hub
- **Cosmos DB Storage**: Store time-series telemetry data
- **Digital Twins Integration**: Synchronize robot state with Azure Digital Twins
- **Alert Engine**: Generate alerts for battery low, temperature high, errors, etc.
- **REST API**: HTTP endpoints for monitoring and control
- **Command Routing**: Forward commands from intent pipeline to robots

## Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Update with your Azure connection strings
   ```

3. **Start Service**
   ```bash
   npm start
   ```

## Environment Configuration

```bash
# Azure IoT Hub Configuration
IOT_HUB_CONNECTION_STRING="HostName=robot-fleet-hub.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=YOUR_KEY"
IOT_HUB_EVENT_HUB_NAME="robot-fleet-hub"

# Azure Cosmos DB Configuration
COSMOS_DB_ENDPOINT="https://robot-fleet-cosmos.documents.azure.com:443/"
COSMOS_DB_KEY="YOUR_PRIMARY_KEY"
COSMOS_DB_DATABASE="robot-fleet-db"
COSMOS_DB_CONTAINER="telemetry"

# Azure Digital Twins Configuration
DIGITAL_TWINS_ENDPOINT="https://robot-fleet-digital-twins.api.eus.digitaltwins.azure.net"

# Service Configuration
PORT=3001
LOG_LEVEL=info
TELEMETRY_BATCH_SIZE=10
TELEMETRY_BATCH_TIMEOUT_MS=5000

# Alert Configuration
BATTERY_LOW_THRESHOLD=20
TEMPERATURE_HIGH_THRESHOLD=80
CONNECTION_TIMEOUT_SECONDS=30
ERROR_RATE_THRESHOLD=0.1

# Intent Pipeline Configuration
INTENT_PIPELINE_URL="http://localhost:3002"
COMMAND_RETRY_ATTEMPTS=3
COMMAND_RETRY_DELAY_MS=1000
```

## API Endpoints

### Health & Status
- `GET /health` - Service health check
- `GET /stats` - Processing statistics

### Robot Management
- `GET /robots` - Get all robot status
- `GET /robots/:robotId` - Get specific robot status
- `POST /robots/:robotId/commands` - Send command to robot

### Alerts
- `GET /alerts` - Get all active alerts
- `GET /alerts?robotId=robot-001` - Get alerts for specific robot
- `POST /alerts/:alertId/acknowledge` - Acknowledge alert
- `POST /alerts/:alertId/resolve` - Resolve alert
- `GET /alerts/statistics` - Get alert statistics

### Digital Twins
- `GET /digitaltwins/robots` - Get all robot twins
- `GET /digitaltwins/zones` - Get all zone twins
- `GET /digitaltwins/zones/:zoneId/robots` - Get robots in specific zone
- `POST /digitaltwins/tasks` - Create task twin

## Digital Twins Models

### Robot Model
```json
{
  "@id": "dtmi:robotfleet:Robot;1",
  "displayName": "Robot",
  "contents": [
    {"name": "batteryLevel", "schema": "double"},
    {"name": "status", "schema": "string"},
    {"name": "temperature", "schema": "double"},
    {"name": "currentTask", "schema": "string"},
    {"name": "lastSeen", "schema": "dateTime"}
  ]
}
```

### Zone Model
```json
{
  "@id": "dtmi:robotfleet:Zone;1",
  "displayName": "Zone",
  "contents": [
    {"name": "name", "schema": "string"},
    {"name": "coordinates", "schema": "map"},
    {"name": "capacity", "schema": "integer"},
    {"name": "currentOccupancy", "schema": "integer"}
  ]
}
```

### Task Model
```json
{
  "@id": "dtmi:robotfleet:Task;1",
  "displayName": "Task",
  "contents": [
    {"name": "taskId", "schema": "string"},
    {"name": "type", "schema": "string"},
    {"name": "status", "schema": "string"},
    {"name": "priority", "schema": "integer"},
    {"name": "createdAt", "schema": "dateTime"}
  ]
}
```

## Alert Types

### Battery Alerts
- **Warning**: Battery < 20%
- **Critical**: Battery < 10%

### Temperature Alerts
- **Warning**: Temperature > 80°C
- **Critical**: Temperature > 90°C

### Connection Alerts
- **Critical**: No telemetry for 30+ seconds

### Error Alerts
- **Error**: Robot status = "error"
- **Warning**: High error rate > 10%

## Command Examples

### Send Command to Robot
```bash
curl -X POST http://localhost:3001/robots/robot-001/commands \
  -H "Content-Type: application/json" \
  -d '{
    "command": "move_to",
    "parameters": {"x": 10.0, "y": 20.0, "z": 0.0}
  }'
```

### Get Robot Status
```bash
curl http://localhost:3001/robots/robot-001
```

### Get Active Alerts
```bash
curl http://localhost:3001/alerts
```

## Processing Pipeline

1. **IoT Hub Ingestion**: Receive telemetry from robot devices
2. **Validation**: Verify telemetry format and values
3. **Storage**: Store in Cosmos DB with partition key (robotId)
4. **Digital Twins Sync**: Update twin properties
5. **Alert Generation**: Check thresholds and conditions
6. **Intent Pipeline**: Forward alerts and status updates

## Performance Metrics

- **Message Latency**: < 1 second from robot to storage
- **Throughput**: 1000+ messages per second
- **Storage**: Time-series data with 1-second granularity
- **Alerts**: Real-time generation and notification

## Monitoring

### Health Check
```bash
curl http://localhost:3001/health
```

### Processing Statistics
```bash
curl http://localhost:3001/stats
```

### Alert Statistics
```bash
curl http://localhost:3001/alerts/statistics
```

## Docker Deployment

```bash
# Build image
npm run docker:build

# Run container
npm run docker:run
```

## Integration with Intent Pipeline

The Event Processor integrates with your existing intent pipeline through:

1. **Alert Forwarding**: Send alerts to intent pipeline for AI processing
2. **Command Routing**: Receive commands from intent pipeline and forward to robots
3. **Context Data**: Provide robot status for intent understanding
4. **Feedback Loop**: Confirm command execution via telemetry

## Troubleshooting

### Common Issues

**Connection Issues**
- Verify Azure connection strings
- Check network connectivity
- Ensure Azure services are provisioned

**Processing Delays**
- Monitor batch size and timeout settings
- Check Cosmos DB throughput
- Verify Digital Twins service availability

**Alert Flood**
- Adjust alert thresholds
- Implement alert deduplication
- Monitor error rates

### Debug Commands
```bash
# Check service logs
docker logs event-processor

# Test IoT Hub connection
az iot hub show-connection-string --name robot-fleet-hub

# Test Cosmos DB connection
az cosmosdb keys list --name robot-fleet-cosmos
```

## Architecture

```
Robot Simulators → IoT Hub → Event Processor → Cosmos DB → Digital Twins
                                    ↓
                              Alert Engine → Intent Pipeline
                                    ↓
                              REST API → Dashboard
```

## Next Steps

1. **Deploy to Azure Container Apps**
2. **Integrate with Intent Pipeline**
3. **Build Dashboard Visualization**
4. **Add Advanced Analytics**
5. **Implement Predictive Maintenance**
