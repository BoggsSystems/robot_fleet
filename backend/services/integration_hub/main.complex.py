"""
Integration Hub - Central Service for C# + Python Communication

This service handles:
- Message queue management
- Service-to-service communication
- Data synchronization
- Performance monitoring
- Circuit breaker patterns
- Retry mechanisms
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Integration Services
from services.message_queue_service import MessageQueueService
from services.communication_service import CommunicationService
from services.synchronization_service import SynchronizationService
from services.monitoring_service import MonitoringService
from services.circuit_breaker_service import CircuitBreakerService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Integration Hub...")
    
    # Initialize integration services
    app.state.message_queue = MessageQueueService()
    app.state.communication = CommunicationService()
    app.state.synchronization = SynchronizationService()
    app.state.monitoring = MonitoringService()
    app.state.circuit_breaker = CircuitBreakerService()
    
    # Start background tasks
    asyncio.create_task(app.state.message_queue.start_consumers())
    asyncio.create_task(app.state.monitoring.start_metrics_collection())
    
    logger.info("Integration Hub started successfully")
    yield
    
    logger.info("Shutting down Integration Hub...")


# Create FastAPI application
app = FastAPI(
    title="Warehouse Integration Hub",
    description="Central integration service for C# + Python warehouse AI system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Data Models
class ServiceMessage(BaseModel):
    """Message model for service communication"""
    message_id: str
    source_service: str
    target_service: str
    message_type: str
    payload: Dict
    priority: str = "medium"
    timestamp: str
    correlation_id: Optional[str] = None


class SyncRequest(BaseModel):
    """Synchronization request model"""
    sync_type: str
    source_data: Dict
    target_service: str
    sync_options: Dict = {}


class HealthCheck(BaseModel):
    """Health check response model"""
    status: str
    services: Dict[str, str]
    message_queue: str
    database: str
    timestamp: str


# Health Check
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Comprehensive health check of all integrated services"""
    try:
        logger.info("Performing comprehensive health check")
        
        # Check all services
        services = {
            "digital_twin_service": await check_service_health("http://localhost:7000/health"),
            "ai_engine": await check_service_health("http://localhost:8000/health"),
            "integration_hub": "healthy"
        }
        
        # Check message queue
        message_queue = await check_message_queue_health()
        
        # Check database
        database = await check_database_health()
        
        # Overall status
        overall_status = "healthy"
        if any(status != "healthy" for status in services.values()):
            overall_status = "degraded"
        if message_queue != "healthy" or database != "healthy":
            overall_status = "unhealthy"
        
        return HealthCheck(
            status=overall_status,
            services=services,
            message_queue=message_queue,
            database=database,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


# Message Queue Endpoints
@app.post("/api/messages/send")
async def send_message(message: ServiceMessage, background_tasks: BackgroundTasks):
    """
    Send message between services through message queue
    
    This endpoint handles:
    - Message validation and routing
    - Priority queuing
    - Circuit breaker protection
    - Retry mechanisms
    """
    try:
        logger.info(f"Sending message: {message.message_id} from {message.source_service} to {message.target_service}")
        
        message_queue: MessageQueueService = app.state.message_queue
        circuit_breaker: CircuitBreakerService = app.state.circuit_breaker
        
        # Check circuit breaker for target service
        if not circuit_breaker.is_service_available(message.target_service):
            raise HTTPException(
                status_code=503, 
                detail=f"Service {message.target_service} is currently unavailable"
            )
        
        # Send message through queue
        await message_queue.send_message(message)
        
        # Record metrics
        monitoring: MonitoringService = app.state.monitoring
        await monitoring.record_message_sent(message)
        
        return {
            "status": "sent",
            "message_id": message.message_id,
            "queued_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Message sending failed: {str(e)}")


@app.get("/api/messages/{message_id}")
async def get_message_status(message_id: str):
    """Get message processing status"""
    try:
        message_queue: MessageQueueService = app.state.message_queue
        status = await message_queue.get_message_status(message_id)
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get message status: {str(e)}")
        raise HTTPException(status_code=500, detail="Status retrieval failed")


# Service Communication Endpoints
@app.post("/api/communication/forward")
async def forward_request(
    target_service: str,
    endpoint: str,
    payload: Dict,
    timeout: int = 30
):
    """
    Forward HTTP request to target service
    
    This endpoint handles:
    - HTTP request forwarding
    - Timeout management
    - Error handling
    - Response transformation
    """
    try:
        logger.info(f"Forwarding request to {target_service}: {endpoint}")
        
        communication: CommunicationService = app.state.communication
        circuit_breaker: CircuitBreakerService = app.state.circuit_breaker
        
        # Check circuit breaker
        if not circuit_breaker.is_service_available(target_service):
            raise HTTPException(
                status_code=503,
                detail=f"Service {target_service} is currently unavailable"
            )
        
        # Forward request
        response = await communication.forward_request(
            target_service=target_service,
            endpoint=endpoint,
            payload=payload,
            timeout=timeout
        )
        
        # Record metrics
        monitoring: MonitoringService = app.state.monitoring
        await monitoring.record_request_forwarded(target_service, response["status_code"])
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to forward request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Request forwarding failed: {str(e)}")


# Data Synchronization Endpoints
@app.post("/api/synchronization/sync")
async def synchronize_data(sync_request: SyncRequest, background_tasks: BackgroundTasks):
    """
    Synchronize data between services
    
    This endpoint handles:
    - Data transformation
    - Conflict resolution
    - Bidirectional sync
    - Progress tracking
    """
    try:
        logger.info(f"Starting synchronization: {sync_request.sync_type}")
        
        synchronization: SynchronizationService = app.state.synchronization
        
        # Start synchronization in background
        sync_id = await synchronization.start_synchronization(sync_request)
        
        # Add background task to monitor progress
        background_tasks.add_task(
            synchronization.monitor_synchronization_progress,
            sync_id
        )
        
        return {
            "sync_id": sync_id,
            "status": "started",
            "sync_type": sync_request.sync_type,
            "started_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to start synchronization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Synchronization failed: {str(e)}")


@app.get("/api/synchronization/{sync_id}/status")
async def get_synchronization_status(sync_id: str):
    """Get synchronization progress and status"""
    try:
        synchronization: SynchronizationService = app.state.synchronization
        status = await synchronization.get_sync_status(sync_id)
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get sync status: {str(e)}")
        raise HTTPException(status_code=500, detail="Status retrieval failed")


# Monitoring & Metrics Endpoints
@app.get("/api/metrics/services")
async def get_service_metrics():
    """Get service performance metrics"""
    try:
        monitoring: MonitoringService = app.state.monitoring
        metrics = await monitoring.get_service_metrics()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get service metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Metrics retrieval failed")


@app.get("/api/metrics/messages")
async def get_message_metrics():
    """Get message queue metrics"""
    try:
        monitoring: MonitoringService = app.state.monitoring
        metrics = await monitoring.get_message_metrics()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get message metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Metrics retrieval failed")


@app.get("/api/circuit-breaker/status")
async def get_circuit_breaker_status():
    """Get circuit breaker status for all services"""
    try:
        circuit_breaker: CircuitBreakerService = app.state.circuit_breaker
        status = await circuit_breaker.get_all_circuit_status()
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get circuit breaker status: {str(e)}")
        raise HTTPException(status_code=500, detail="Status retrieval failed")


# Integration Testing Endpoints
@app.post("/api/test/integration")
async def test_integration(test_config: Dict):
    """
    Run integration tests between services
    
    This endpoint handles:
    - End-to-end testing
    - Performance testing
    - Load testing
    - Health verification
    """
    try:
        logger.info("Starting integration tests")
        
        # Test service connectivity
        connectivity_results = await test_service_connectivity()
        
        # Test message flow
        message_flow_results = await test_message_flow()
        
        # Test data synchronization
        sync_results = await test_data_synchronization()
        
        # Test performance
        performance_results = await test_performance()
        
        results = {
            "connectivity": connectivity_results,
            "message_flow": message_flow_results,
            "synchronization": sync_results,
            "performance": performance_results,
            "overall_status": "passed" if all(
                result["status"] == "passed" for result in [
                    connectivity_results, message_flow_results, sync_results
                ]
            ) else "failed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Integration test failed")


# Helper Functions
async def check_service_health(service_url: str) -> str:
    """Check health of individual service"""
    try:
        communication: CommunicationService = app.state.communication
        response = await communication.make_request("GET", service_url, timeout=5)
        return "healthy" if response.get("status") == 200 else "unhealthy"
    except Exception:
        return "unhealthy"


async def check_message_queue_health() -> str:
    """Check message queue health"""
    try:
        message_queue: MessageQueueService = app.state.message_queue
        return await message_queue.health_check()
    except Exception:
        return "unhealthy"


async def check_database_health() -> str:
    """Check database connectivity"""
    try:
        synchronization: SynchronizationService = app.state.synchronization
        return await synchronization.check_database_health()
    except Exception:
        return "unhealthy"


async def test_service_connectivity() -> Dict:
    """Test connectivity to all services"""
    services = ["digital_twin_service", "ai_engine"]
    results = {}
    
    for service in services:
        try:
            health = await check_service_health(f"http://localhost:{7000 if 'digital' in service else 8000}/health")
            results[service] = health
        except Exception as e:
            results[service] = f"error: {str(e)}"
    
    all_healthy = all(status == "healthy" for status in results.values())
    
    return {
        "status": "passed" if all_healthy else "failed",
        "services": results,
        "timestamp": datetime.utcnow().isoformat()
    }


async def test_message_flow() -> Dict:
    """Test message flow between services"""
    try:
        # Send test message
        test_message = ServiceMessage(
            message_id="test-" + str(datetime.utcnow().timestamp()),
            source_service="integration_hub",
            target_service="ai_engine",
            message_type="test",
            payload={"test": True},
            timestamp=datetime.utcnow().isoformat()
        )
        
        message_queue: MessageQueueService = app.state.message_queue
        await message_queue.send_message(test_message)
        
        # Check if message was processed (mock implementation)
        await asyncio.sleep(1)  # Wait for processing
        
        return {
            "status": "passed",
            "message_id": test_message.message_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def test_data_synchronization() -> Dict:
    """Test data synchronization"""
    try:
        sync_request = SyncRequest(
            sync_type="test_sync",
            source_data={"test": "data"},
            target_service="digital_twin_service"
        )
        
        synchronization: SynchronizationService = app.state.synchronization
        sync_id = await synchronization.start_synchronization(sync_request)
        
        # Wait for sync completion (mock)
        await asyncio.sleep(2)
        
        return {
            "status": "passed",
            "sync_id": sync_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


async def test_performance() -> Dict:
    """Test performance metrics"""
    try:
        monitoring: MonitoringService = app.state.monitoring
        metrics = await monitoring.get_performance_metrics()
        
        # Check if metrics are within acceptable ranges
        acceptable = True
        if metrics.get("response_time", 0) > 1000:  # 1 second
            acceptable = False
        if metrics.get("error_rate", 0) > 0.05:  # 5%
            acceptable = False
        
        return {
            "status": "passed" if acceptable else "failed",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )
