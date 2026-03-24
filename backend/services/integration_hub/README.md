# 🔄 Warehouse Integration Hub

## 📋 Overview

This service acts as the central nervous system for the C# + Python warehouse AI system, handling communication, synchronization, monitoring, and fault tolerance between all services.

## 🏗️ Architecture

### **Core Components**
- **MessageQueueService**: Multi-backend message queuing (Azure Service Bus, Redis, RabbitMQ)
- **CommunicationService**: HTTP communication with circuit breaker patterns
- **SynchronizationService**: Data synchronization with conflict resolution
- **MonitoringService**: Performance metrics and distributed tracing
- **CircuitBreakerService**: Fault tolerance and automatic recovery

### **Key Features**
- ✅ **Multi-Backend Message Queues**: Azure Service Bus, Redis, RabbitMQ support
- ✅ **Circuit Breaker Patterns**: Automatic fault detection and recovery
- ✅ **Data Synchronization**: Bidirectional sync with conflict resolution
- ✅ **Performance Monitoring**: Prometheus metrics and distributed tracing
- ✅ **Health Monitoring**: Comprehensive service health tracking
- ✅ **Load Balancing**: Intelligent request routing and failover

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- Azure Services (Service Bus, Cosmos DB) - optional
- Redis - optional
- PostgreSQL - optional
- Sufficient memory for monitoring data

### **Installation**

```bash
cd services/integration_hub
pip install -r requirements.txt
```

### **Configuration**

Create `.env` file:
```bash
# Azure Services
AZURE_SERVICE_BUS_CONNECTION=your-service-bus-connection-string
AZURE_COSMOS_ENDPOINT=your-cosmos-endpoint
AZURE_COSMOS_KEY=your-cosmos-key

# Message Queue
REDIS_HOST=localhost
REDIS_PORT=6379
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672

# Database
SQL_DATABASE_CONNECTION=postgresql://user:pass@localhost/warehouse_sync

# Monitoring
PROMETHEUS_ENABLED=true
OPENTELEMETRY_ENABLED=true
LOG_LEVEL=INFO
```

### **Running the Service**

```bash
# Development mode
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 9000 --workers 4
```

## 📚 API Documentation

### **Base URL**: `http://localhost:9000`

### **Endpoints**

#### **Health & Monitoring**

**Comprehensive Health Check**
```http
GET /health
```
Returns health status of all integrated services, message queues, and databases.

**Service Metrics**
```http
GET /api/metrics/services
```
Returns performance metrics for all services.

**Message Metrics**
```http
GET /api/metrics/messages
```
Returns message queue performance metrics.

**Circuit Breaker Status**
```http
GET /api/circuit-breaker/status
```
Returns circuit breaker status for all services.

#### **Message Queue Operations**

**Send Message**
```http
POST /api/messages/send
Content-Type: application/json

{
  "message_id": "msg-001",
  "source_service": "integration_hub",
  "target_service": "ai_engine",
  "message_type": "mission_request",
  "payload": {
    "request_text": "Pick items from zone B",
    "priority": "high"
  },
  "priority": "high",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Get Message Status**
```http
GET /api/messages/{message_id}
```

#### **Service Communication**

**Forward Request**
```http
POST /api/communication/forward
Content-Type: application/json

{
  "target_service": "ai_engine",
  "endpoint": "/api/ai/mission-plan",
  "payload": {
    "request_id": "req-001",
    "request_text": "Pick 5 items from zone B"
  },
  "timeout": 30
}
```

#### **Data Synchronization**

**Start Synchronization**
```http
POST /api/synchronization/sync
Content-Type: application/json

{
  "sync_type": "bidirectional",
  "source_data": {
    "warehouse_id": "warehouse-001",
    "zones": [...],
    "robots": [...]
  },
  "target_service": "digital_twin_service",
  "sync_options": {
    "entity_type": "warehouse_config",
    "conflict_resolution": "last_write_wins"
  }
}
```

**Get Sync Status**
```http
GET /api/synchronization/{sync_id}/status
```

#### **Integration Testing**

**Run Integration Tests**
```http
POST /api/test/integration
Content-Type: application/json

{
  "test_config": {
    "connectivity_check": true,
    "message_flow_test": true,
    "synchronization_test": true,
    "performance_test": true
  }
}
```

## 🔧 Service Architecture

### **Communication Flow**
```
🏭 C# Digital Twin ←→ 🔄 Integration Hub ←→ 🧠 Python AI Engine
         ↓                    ↓                    ↓
    HTTP APIs           Message Queues        HTTP APIs
    REST Endpoints      Service Bus           REST Endpoints
    JSON Data           Redis/RabbitMQ        JSON Data
```

### **Message Queue Backends**
```
📡 Azure Service Bus (Primary)
├── High throughput
├── Enterprise features
├── Dead letter queues
└── Geo-replication

🔄 Redis Pub/Sub (Secondary)
├── Low latency
├── In-memory caching
├── Pub/Sub patterns
└── Lightweight

🐰 RabbitMQ (Tertiary)
├── AMQP protocol
├── Message routing
├── Queue management
└── Open source
```

### **Circuit Breaker States**
```
🟢 CLOSED: Normal operation
🔴 OPEN: Blocking calls (service unhealthy)
🟡 HALF_OPEN: Testing recovery
```

## 📊 Monitoring & Observability

### **Metrics Collection**
- **Request Metrics**: Count, duration, error rate
- **System Metrics**: CPU, memory, disk, network
- **Business Metrics**: Robots active, tasks completed, throughput
- **Queue Metrics**: Message depth, processing time, failure rate

### **Distributed Tracing**
- **Request Tracing**: End-to-end request flow
- **Service Dependencies**: Service call graphs
- **Performance Analysis**: Bottleneck identification
- **Error Tracking**: Error propagation analysis

### **Alert Management**
- **Threshold Alerts**: Performance threshold violations
- **Health Alerts**: Service health changes
- **Circuit Breaker Alerts**: Circuit state changes
- **Custom Alerts**: Business logic alerts

## 🔧 Development

### **Project Structure**
```
services/integration_hub/
├── main.py                           # FastAPI application
├── requirements.txt                   # Python dependencies
├── services/
│   ├── message_queue_service.py       # Message queue management
│   ├── communication_service.py      # HTTP communication
│   ├── synchronization_service.py     # Data synchronization
│   ├── monitoring_service.py         # Performance monitoring
│   └── circuit_breaker_service.py    # Fault tolerance
├── models/
│   ├── integration_models.py         # Data models
│   └── monitoring_models.py          # Monitoring models
├── utils/
│   ├── retry.py                      # Retry utilities
│   ├── serialization.py              # Data serialization
│   └── validation.py                 # Input validation
├── tests/
│   ├── test_message_queue.py         # Message queue tests
│   ├── test_communication.py         # Communication tests
│   └── test_synchronization.py       # Synchronization tests
└── README.md
```

### **Running Tests**

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_message_queue.py

# Run with coverage
pytest --cov=services tests/
```

### **Code Quality**

```bash
# Format code
black .

# Lint code
flake8 services/

# Type checking
mypy services/
```

## 🔄 Integration Patterns

### **Message Queue Integration**
```python
# Send message to AI engine
message = ServiceMessage(
    message_id="msg-001",
    source_service="digital_twin_service",
    target_service="ai_engine",
    message_type="telemetry_update",
    payload={"robot_id": "robot-001", "status": "busy"},
    priority="medium",
    timestamp=datetime.utcnow().isoformat()
)

await message_queue.send_message(message)
```

### **HTTP Communication**
```python
# Forward request with circuit breaker
response = await communication.forward_request(
    target_service="ai_engine",
    endpoint="/api/ai/mission-plan",
    payload=request_data,
    timeout=30
)
```

### **Data Synchronization**
```python
# Sync warehouse configuration
sync_request = SyncRequest(
    sync_type="bidirectional",
    source_data=warehouse_config,
    target_service="digital_twin_service",
    sync_options={"conflict_resolution": "last_write_wins"}
)

sync_id = await synchronization.start_synchronization(sync_request)
```

## 📊 Performance Optimization

### **Circuit Breaker Tuning**
```python
# Configure circuit breaker for high-traffic service
config = CircuitBreakerConfig(
    failure_threshold=10,      # More failures before opening
    recovery_timeout=30,       # Faster recovery
    success_threshold=5,       # More successes to close
    timeout=15,               # Shorter timeout
    degradation_threshold=0.15  # Lower degradation threshold
)

circuit_breaker.register_service("ai_engine", config)
```

### **Message Queue Optimization**
```python
# Priority-based message routing
high_priority_message = ServiceMessage(
    message_id="urgent-001",
    priority="critical",
    # ... other fields
)

# Backend selection based on message type
backend = "azure" if priority == "critical" else "redis"
await message_queue.send_message(message, backend=backend)
```

## 🔍 Troubleshooting

### **Common Issues**

**Circuit Breaker Always Open**
```bash
# Check circuit breaker status
curl http://localhost:9000/api/circuit-breaker/status

# Reset circuit breaker
curl -X POST http://localhost:9000/api/circuit-breaker/reset/ai_engine
```

**Message Queue Backlog**
```bash
# Check queue metrics
curl http://localhost:9000/api/metrics/messages

# Increase consumer count
# Update configuration and restart service
```

**Synchronization Conflicts**
```bash
# Check sync status
curl http://localhost:9000/api/synchronization/{sync_id}/status

# Review conflict resolution strategy
# Update sync_options in synchronization request
```

### **Health Check Failures**
```bash
# Comprehensive health check
curl http://localhost:9000/health

# Check individual service health
curl http://localhost:7000/health  # C# service
curl http://localhost:8000/health  # Python AI service
```

## 🚀 Deployment

### **Docker**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 9000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
```

### **Azure Container Apps**
```bash
# Build and push
az acr build --registry your-registry --image warehouse-integration-hub .

# Deploy
az containerapp create \
  --name warehouse-integration-hub \
  --resource-group warehouse-ai-rg \
  --image your-registry/warehouse-integration-hub:latest \
  --cpu 1 \
  --memory 2Gi \
  --env-vars \
    AZURE_SERVICE_BUS_CONNECTION=your-connection \
    LOG_LEVEL=INFO
```

### **Kubernetes**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: integration-hub
spec:
  replicas: 3
  selector:
    matchLabels:
      app: integration-hub
  template:
    metadata:
      labels:
        app: integration-hub
    spec:
      containers:
      - name: integration-hub
        image: your-registry/warehouse-integration-hub:latest
        ports:
        - containerPort: 9000
        env:
        - name: AZURE_SERVICE_BUS_CONNECTION
          valueFrom:
            secretKeyRef:
              name: warehouse-secrets
              key: service-bus-connection
```

## 🔧 Configuration

### **Environment Variables**
```bash
# Message Queue Configuration
AZURE_SERVICE_BUS_CONNECTION=your-connection-string
REDIS_HOST=localhost
REDIS_PORT=6379
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672

# Database Configuration
AZURE_COSMOS_ENDPOINT=your-cosmos-endpoint
AZURE_COSMOS_KEY=your-cosmos-key
SQL_DATABASE_CONNECTION=postgresql://user:pass@localhost/warehouse_sync

# Monitoring Configuration
PROMETHEUS_ENABLED=true
OPENTELEMETRY_ENABLED=true
METRICS_COLLECTION_INTERVAL=15

# Circuit Breaker Configuration
DEFAULT_FAILURE_THRESHOLD=5
DEFAULT_RECOVERY_TIMEOUT=60
DEFAULT_SUCCESS_THRESHOLD=3
DEFAULT_TIMEOUT=30
```

### **Service Configuration**
```python
# Custom circuit breaker configuration
custom_config = CircuitBreakerConfig(
    failure_threshold=8,
    recovery_timeout=45,
    success_threshold=4,
    timeout=20,
    degradation_threshold=0.25
)

circuit_breaker.register_service("critical_service", custom_config)
```

## 🎯 Best Practices

### **Message Queue Design**
- Use appropriate backend for each use case
- Implement message prioritization
- Handle dead letter queues
- Monitor queue depth and processing time

### **Circuit Breaker Usage**
- Set appropriate thresholds for each service
- Monitor circuit state changes
- Implement fallback mechanisms
- Use half-open state for testing recovery

### **Data Synchronization**
- Choose appropriate conflict resolution strategy
- Implement incremental synchronization
- Monitor sync performance
- Handle large datasets efficiently

### **Monitoring & Alerting**
- Set meaningful alert thresholds
- Monitor business metrics, not just technical metrics
- Implement distributed tracing for debugging
- Use structured logging for better analysis

## 📞 Support

For questions or issues:
- Check the [API documentation](http://localhost:9000/docs)
- Review the [implementation plan](../../IMPLEMENTATION_PLAN.md)
- Consult the [architecture documentation](../../WAREHOUSE_ARCHITECTURE.md)

---

*Service Version: 1.0.0*  
*Last Updated: 2026-03-23*
