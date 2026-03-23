# 🧠 Warehouse AI Engine

## 📋 Overview

This Python service provides advanced AI capabilities for warehouse fleet management, including intent understanding, mission planning, RAG (Retrieval-Augmented Generation), analytics, and optimization.

## 🏗️ Architecture

### **Core Components**
- **IntentService**: Natural language understanding and intent parsing
- **RAGService**: Knowledge base management and semantic search
- **AnalyticsService**: Predictive analytics and performance metrics
- **OptimizationService**: Fleet and workflow optimization
- **FastAPI**: REST API framework for C# integration

### **Key Features**
- ✅ **Intent Understanding**: Parse natural language warehouse requests
- ✅ **Mission Planning**: Generate optimal robot task assignments
- ✅ **RAG System**: Semantic search across warehouse knowledge
- ✅ **Predictive Analytics**: Maintenance, performance, and inventory predictions
- ✅ **Fleet Optimization**: Real-time fleet optimization recommendations
- ✅ **Workflow Optimization**: Process improvement recommendations
- ✅ **C# Integration**: REST API for seamless C# service communication

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+
- CUDA (optional, for GPU acceleration)
- Sufficient RAM for ML models (8GB+ recommended)

### **Installation**

```bash
cd services/ai_engine
pip install -r requirements.txt
```

### **Configuration**

Create `.env` file:
```bash
OPENAI_API_KEY=your-openai-api-key
AZURE_COSMOS_ENDPOINT=your-cosmos-endpoint
AZURE_SERVICE_BUS_CONNECTION=your-service-bus-connection
LOG_LEVEL=INFO
```

### **Running the Service**

```bash
# Development mode
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Documentation

### **Base URL**: `http://localhost:8000`

### **Endpoints**

#### **AI Decision Engine**

**Generate Mission Plan**
```http
POST /api/ai/mission-plan
Content-Type: application/json

{
  "request_id": "req-001",
  "request_text": "Pick 5 items from zone B and bring them to packing",
  "priority": "high",
  "constraints": {
    "deadline": "2024-01-01T15:00:00Z"
  },
  "current_state": {
    "zone_b_occupancy": 45,
    "available_robots": 3
  },
  "context": {
    "zone_type": "picking",
    "operation_type": "fulfillment"
  }
}
```

**Parse Intent**
```http
POST /api/ai/intent-parse
Content-Type: application/json

{
  "request_id": "req-002",
  "request_text": "Check inventory levels in receiving zone",
  "priority": "medium",
  "context": {
    "zone_type": "receiving"
  }
}
```

#### **RAG System**

**Search Knowledge**
```http
POST /api/rag/search
Content-Type: application/json

{
  "query": "How to handle emergency robot maintenance",
  "context": {
    "zone_type": "maintenance",
    "robot_type": "humanoid"
  },
  "max_results": 5
}
```

**Add Knowledge**
```http
POST /api/rag/add-knowledge
Content-Type: application/json

{
  "content": "Emergency maintenance procedure: 1) Stop robot operations 2) Secure area 3) Call technician",
  "metadata": {
    "source": "maintenance_manual",
    "category": "emergency",
    "priority": "high"
  }
}
```

#### **Analytics Engine**

**Generate Predictions**
```http
POST /api/analytics/predict
Content-Type: application/json

{
  "prediction_type": "maintenance",
  "parameters": {
    "robot_id": "robot-001",
    "current_hours": 850
  },
  "time_horizon": "24h"
}
```

**Get Performance Metrics**
```http
GET /api/analytics/performance
```

**Get Trend Analysis**
```http
GET /api/analytics/performance/trend?metric=throughput&period=7d
```

#### **Optimization Engine**

**Optimize Fleet**
```http
POST /api/optimization/fleet
Content-Type: application/json

{
  "robots": [
    {
      "id": "robot-001",
      "type": "humanoid",
      "battery_level": 85,
      "status": "idle",
      "location": [10, 15, 0]
    }
  ],
  "tasks": [
    {
      "id": "task-001",
      "type": "picking",
      "priority": "high",
      "location": [20, 25, 0]
    }
  ]
}
```

**Optimize Workflow**
```http
POST /api/optimization/workflow
Content-Type: application/json

{
  "zones": [
    {
      "id": "zone_b_picking",
      "current_occupancy": 45,
      "capacity": 200,
      "queue_length": 8
    }
  ],
  "current_throughput": 1250,
  "target_throughput": 1500
}
```

## 🏗️ Data Models

### **Warehouse Request**
```python
class WarehouseRequest(BaseModel):
    request_id: str
    request_text: str
    priority: str = "medium"
    constraints: Dict = {}
    current_state: Dict = {}
    context: Dict = {}
```

### **Mission Plan**
```python
class MissionPlan(BaseModel):
    mission_id: str
    robot_assignments: List[Dict]
    estimated_duration: int
    confidence_score: float
    optimization_notes: str
    alternative_plans: List[Dict] = []
```

### **Knowledge Result**
```python
class KnowledgeResult(BaseModel):
    content: str
    source: str
    relevance_score: float
    metadata: Dict = {}
```

### **Prediction Result**
```python
class PredictionResult(BaseModel):
    prediction_id: str
    prediction_type: str
    results: Dict
    confidence: float
    timestamp: str
```

## 🔧 Development

### **Project Structure**
```
services/ai_engine/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── services/
│   ├── intent_service.py   # Intent understanding
│   ├── rag_service.py      # RAG system
│   ├── analytics_service.py # Predictive analytics
│   └── optimization_service.py # Optimization algorithms
├── models/
│   ├── warehouse_models.py # Data models
│   └── ai_models.py       # ML model interfaces
├── utils/
│   ├── embeddings.py      # Embedding utilities
│   └── preprocessing.py   # Text preprocessing
├── tests/
│   ├── test_intent.py      # Intent service tests
│   ├── test_rag.py         # RAG service tests
│   └── test_analytics.py   # Analytics service tests
└── README.md
```

### **Running Tests**

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_intent.py

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

## 🔍 AI Capabilities

### **Intent Understanding**
- **Rule-based parsing**: Pattern matching for common warehouse requests
- **ML-based classification**: Transformer models for intent classification
- **Context-aware reasoning**: Incorporates warehouse state and context
- **Entity extraction**: Identifies locations, quantities, priorities, constraints

### **RAG System**
- **Vector embeddings**: Sentence transformers for semantic search
- **ChromaDB**: Vector database for efficient similarity search
- **Knowledge management**: Add, update, delete knowledge entries
- **Context enhancement**: Query enhancement with warehouse context

### **Predictive Analytics**
- **Maintenance prediction**: Predictive maintenance for robots
- **Performance forecasting**: Throughput and efficiency predictions
- **Inventory forecasting**: Demand prediction and stockout risk
- **Anomaly detection**: Identify unusual patterns in operations

### **Optimization Algorithms**
- **Task assignment**: Optimal robot-to-task matching
- **Fleet coordination**: Multi-robot collaboration optimization
- **Workflow optimization**: Process improvement recommendations
- **Resource allocation**: Dynamic resource distribution

## 🔄 C# Integration

### **Communication Patterns**
```python
# C# calling Python AI service
import httpx

async def get_mission_plan(request_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/ai/mission-plan",
            json=request_data
        )
        return response.json()
```

```csharp
// C# calling Python AI service
public class PythonAIClient
{
    private readonly HttpClient _httpClient;
    
    public async Task<MissionPlan> GetMissionPlanAsync(WarehouseRequest request)
    {
        var response = await _httpClient.PostAsJsonAsync(
            "http://localhost:8000/api/ai/mission-plan", 
            request
        );
        return await response.Content.ReadFromJsonAsync<MissionPlan>();
    }
}
```

### **Integration Points**
- **Mission Planning**: C# Digital Twin → Python AI → C# Fleet Coordination
- **Intent Parsing**: C# User Interface → Python AI → C# Task Execution
- **Knowledge Search**: C# Configuration → Python RAG → C# Decision Making
- **Predictions**: C# Telemetry → Python Analytics → C# Alerting

## 📊 Performance Metrics

### **Response Time Targets**
- **Intent Parsing**: <200ms
- **Mission Planning**: <500ms
- **Knowledge Search**: <300ms
- **Predictions**: <1s
- **Optimization**: <2s

### **Accuracy Targets**
- **Intent Classification**: >90% accuracy
- **Entity Extraction**: >85% accuracy
- **Predictive Accuracy**: >80% confidence
- **Optimization Improvement**: >10% efficiency gain

## 🔧 Configuration

### **Environment Variables**
```bash
# AI Models
OPENAI_API_KEY=your-openai-api-key
HUGGINGFACE_API_KEY=your-huggingface-key

# Azure Services
AZURE_COSMOS_ENDPOINT=your-cosmos-endpoint
AZURE_SERVICE_BUS_CONNECTION=your-service-bus-connection

# Application
LOG_LEVEL=INFO
MAX_WORKERS=4
MODEL_CACHE_DIR=./models
VECTOR_DB_PATH=./data/vectors
```

### **Model Configuration**
```python
# Sentence transformer model
EMBEDDING_MODEL="all-MiniLM-L6-v2"

# Intent classification model
INTENT_MODEL="microsoft/DialoGPT-medium"

# Anomaly detection
ANOMALY_CONTAMINATION=0.1
```

## 🚀 Deployment

### **Docker**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Azure Container Apps**
```bash
# Build and push
az acr build --registry your-registry --image warehouse-ai-engine .

# Deploy
az containerapp create \
  --name warehouse-ai-engine \
  --resource-group warehouse-ai-rg \
  --image your-registry/warehouse-ai-engine:latest \
  --cpu 2 \
  --memory 4Gi \
  --env-vars \
    OPENAI_API_KEY=your-key \
    LOG_LEVEL=INFO
```

## 🔍 Monitoring & Logging

### **Structured Logging**
```python
import structlog

logger = structlog.get_logger()
logger.info("Mission plan generated", mission_id=mission_id, confidence=0.92)
```

### **Metrics**
```python
from prometheus_client import Counter, Histogram

mission_plans = Counter('mission_plans_total', 'Total mission plans generated')
planning_duration = Histogram('planning_duration_seconds', 'Mission planning duration')
```

## 🎯 Next Steps

1. **Model Training**: Train custom models on warehouse data
2. **Performance Optimization**: GPU acceleration and model quantization
3. **Advanced Features**: Multi-modal AI (vision + text)
4. **Edge Deployment**: On-premises AI inference
5. **Continuous Learning**: Model retraining with operational data

## 📞 Support

For questions or issues:
- Check the [API documentation](http://localhost:8000/docs)
- Review the [implementation plan](../../IMPLEMENTATION_PLAN.md)
- Consult the [architecture documentation](../../WAREHOUSE_ARCHITECTURE.md)

---

*Service Version: 1.0.0*  
*Last Updated: 2026-03-23*
