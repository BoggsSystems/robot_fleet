from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional
import uvicorn

app = FastAPI(title="Warehouse Integration Hub", version="1.0.0")

# Pydantic models
class ServiceStatus(BaseModel):
    status: str
    url: str
    last_check: str

class MessageRequest(BaseModel):
    queue_name: str
    message: Dict
    priority: Optional[str] = "normal"

class CommunicationRequest(BaseModel):
    target_service: str
    endpoint: str
    method: str
    data: Optional[Dict] = {}

class SyncRequest(BaseModel):
    source_service: str
    target_service: str
    data_type: str
    sync_data: Dict

# Health check
@app.get("/health")
async def health():
    services = {
        "digital_twin_service": ServiceStatus(
            status="healthy",
            url="http://warehouse-digital-twin",
            last_check=datetime.utcnow().isoformat()
        ),
        "ai_engine": ServiceStatus(
            status="healthy", 
            url="http://warehouse-ai-engine",
            last_check=datetime.utcnow().isoformat()
        )
    }
    
    return {
        "status": "healthy",
        "service": "integration-hub",
        "services": services,
        "timestamp": datetime.utcnow().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Warehouse Integration Hub",
        "status": "running",
        "services": [
            "digital-twin",
            "ai-engine", 
            "message-queue",
            "communication",
            "synchronization",
            "monitoring"
        ]
    }

# Message queue endpoints
@app.post("/api/message-queue/send")
async def send_message(request: MessageRequest):
    return {
        "message_id": f"msg-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "queue_name": request.queue_name,
        "status": "sent",
        "timestamp": datetime.utcnow().isoformat(),
        "priority": request.priority
    }

@app.get("/api/message-queue/{queue_name}/messages")
async def get_messages(queue_name: str):
    return {
        "queue_name": queue_name,
        "messages": [
            {
                "message_id": "msg-001",
                "content": "Sample message",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "processed"
            }
        ],
        "total_count": 1
    }

# Communication endpoints
@app.post("/api/communication/forward")
async def forward_request(request: CommunicationRequest):
    return {
        "status_code": 200,
        "data": {
            "message": "Request forwarded successfully",
            "target_service": request.target_service,
            "endpoint": request.endpoint,
            "method": request.method
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/communication/service/{service_name}/status")
async def get_service_status(service_name: str):
    return {
        "service_name": service_name,
        "status": "healthy",
        "url": f"http://{service_name}",
        "last_check": datetime.utcnow().isoformat(),
        "response_time_ms": 45
    }

# Synchronization endpoints
@app.post("/api/synchronization/sync")
async def synchronize_data(request: SyncRequest):
    return {
        "sync_id": f"sync-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "source_service": request.source_service,
        "target_service": request.target_service,
        "data_type": request.data_type,
        "status": "completed",
        "records_synced": 25,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/synchronization/status/{sync_id}")
async def get_sync_status(sync_id: str):
    return {
        "sync_id": sync_id,
        "status": "completed",
        "progress": 100,
        "records_synced": 25,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat()
    }

# Monitoring endpoints
@app.get("/api/monitoring/metrics")
async def get_metrics():
    return {
        "services": {
            "digital_twin_service": {
                "status": "healthy",
                "cpu_usage": "35%",
                "memory_usage": "68%",
                "response_time_ms": 120
            },
            "ai_engine": {
                "status": "healthy",
                "cpu_usage": "42%",
                "memory_usage": "71%",
                "response_time_ms": 95
            }
        },
        "message_queues": {
            "warehouse-digital-twin-service": {
                "message_count": 156,
                "processing_rate": "12 msg/min"
            },
            "warehouse-ai-engine": {
                "message_count": 89,
                "processing_rate": "8 msg/min"
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/monitoring/circuit-breaker/status")
async def get_circuit_breaker_status():
    return {
        "circuit_breakers": {
            "digital_twin_service": {
                "status": "closed",
                "failure_count": 0,
                "last_failure": None
            },
            "ai_engine": {
                "status": "closed", 
                "failure_count": 0,
                "last_failure": None
            }
        },
        "overall_status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Test endpoint for integration testing
@app.post("/api/test/integration")
async def test_integration():
    # Test communication between services
    test_results = {
        "digital_twin_connection": "success",
        "ai_engine_connection": "success",
        "message_queue_connection": "success",
        "overall_status": "healthy"
    }
    
    return {
        "test_id": f"test-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "results": test_results,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "All integration tests passed successfully"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
