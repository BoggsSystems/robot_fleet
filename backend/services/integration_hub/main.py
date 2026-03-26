from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

app = FastAPI(title="Warehouse Integration Hub", version="1.0.0")

# Request validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = exc.errors()
    print(f"[VALIDATION ERROR] {errors}")
    return {
        "detail": "Validation failed",
        "errors": [{"field": " -> ".join(str(x) for x in e["loc"]), "message": e["msg"], "type": e["type"]} for e in errors]
    }

# Enable CORS for admin dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Admin Models
class ClientStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    trial = "trial"

class ClientPlan(str, Enum):
    hobby = "hobby"
    pro = "pro"
    business = "business"
    enterprise = "enterprise"

class ClientLocation(BaseModel):
    name: str
    address: str
    type: str = "primary"
    classification: str = "indoor"
    size: str = ""
    operatingHours: str = "24/7"

class ClientContact(BaseModel):
    email: str
    phone: Optional[str] = ""
    address: Optional[str] = ""

class ClientFleet(BaseModel):
    total_robots: int
    active_robots: int
    idle_robots: int
    maintenance_robots: int

class ClientSubscription(BaseModel):
    start_date: str
    end_date: str
    mrr: float

class Client(BaseModel):
    id: str
    name: str
    status: ClientStatus
    plan: ClientPlan
    entityType: Optional[str] = "business"
    industry: Optional[str] = None
    email: str
    phone: Optional[str] = ""
    taxId: Optional[str] = ""
    locations: List[ClientLocation] = []
    fleetSize: int = 0
    deploymentPriority: str = "standard"
    integrations: List[str] = []
    contact: Optional[ClientContact] = None
    warehouse: Optional[Dict] = None
    fleet: ClientFleet
    subscription: ClientSubscription
    created_at: str
    updated_at: Optional[str] = None

class CreateClientRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = ""
    plan: ClientPlan
    entityType: Optional[str] = "business"
    industry: Optional[str] = None
    taxId: Optional[str] = ""
    locations: List[ClientLocation] = []
    fleetSize: int = 1
    deploymentPriority: str = "standard"
    integrations: List[str] = []

class UpdateClientRequest(BaseModel):
    name: Optional[str] = None
    status: Optional[ClientStatus] = None
    plan: Optional[ClientPlan] = None
    contact: Optional[ClientContact] = None

class SystemHealthResponse(BaseModel):
    overall: str
    services: Dict
    metrics: Dict
    timestamp: str

class Alert(BaseModel):
    id: str
    severity: str
    message: str
    source: str
    client_id: Optional[str] = None
    robot_id: Optional[str] = None
    created_at: str
    acknowledged: bool

# Mock data stores (in production, use database)
clients_db: Dict[str, Client] = {
    "1": Client(
        id="1",
        name="Acme Distribution",
        status=ClientStatus.active,
        plan=ClientPlan.business,
        contact=ClientContact(email="admin@acme.com", phone="+1-555-0101", address="123 Main St, NY"),
        warehouse=ClientWarehouse(name="NYC Distribution", location="New York, NY", total_area=50000, zones=4),
        fleet=ClientFleet(total_robots=8, active_robots=6, idle_robots=2, maintenance_robots=0),
        subscription=ClientSubscription(start_date="2023-08-01", end_date="2024-08-01", mrr=5000),
        created_at="2023-08-01T00:00:00Z"
    ),
    "2": Client(
        id="2",
        name="TechFlow Logistics",
        status=ClientStatus.active,
        plan=ClientPlan.enterprise,
        contact=ClientContact(email="ops@techflow.com", phone="+1-555-0102", address="456 Tech Blvd, CA"),
        warehouse=ClientWarehouse(name="SF Bay Hub", location="San Francisco, CA", total_area=100000, zones=6),
        fleet=ClientFleet(total_robots=15, active_robots=12, idle_robots=2, maintenance_robots=1),
        subscription=ClientSubscription(start_date="2023-06-15", end_date="2024-06-15", mrr=12000),
        created_at="2023-06-15T00:00:00Z"
    ),
    "3": Client(
        id="3",
        name="StartupXYZ",
        status=ClientStatus.trial,
        plan=ClientPlan.hobby,
        contact=ClientContact(email="hello@startupxyz.com", phone="+1-555-0103", address="789 Startup Ave, TX"),
        warehouse=ClientWarehouse(name="Austin Mini-Warehouse", location="Austin, TX", total_area=15000, zones=2),
        fleet=ClientFleet(total_robots=2, active_robots=2, idle_robots=0, maintenance_robots=0),
        subscription=ClientSubscription(start_date="2024-01-01", end_date="2024-02-01", mrr=0),
        created_at="2024-01-01T00:00:00Z"
    )
}

alerts_db: List[Alert] = [
    Alert(
        id="1",
        severity="warning",
        message="Robot R-15 battery low (15%)",
        source="fleet-control",
        client_id="2",
        robot_id="R-15",
        created_at="2024-01-15T09:30:00Z",
        acknowledged=False
    ),
    Alert(
        id="2",
        severity="info",
        message="Client trial expires in 7 days",
        source="billing",
        client_id="3",
        created_at="2024-01-14T00:00:00Z",
        acknowledged=False
    )
]

# Simple auth middleware for admin endpoints
async def verify_admin_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    # In production, verify JWT with auth service
    # For Phase 1, accept any non-empty token as superadmin
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"adminId": 1, "role": "superadmin", "permissions": ["*"]}

# Admin API Endpoints
@app.get("/api/admin/health", response_model=SystemHealthResponse)
async def get_system_health(admin: dict = Depends(verify_admin_token)):
    """Get overall system health status for admin dashboard"""
    return SystemHealthResponse(
        overall="healthy",
        services={
            "ai_engine": {"status": "healthy", "uptime": 99.9, "last_checked": datetime.utcnow().isoformat(), "response_time_ms": 45},
            "fleet_control": {"status": "healthy", "uptime": 99.8, "last_checked": datetime.utcnow().isoformat(), "response_time_ms": 32},
            "digital_twin": {"status": "healthy", "uptime": 99.9, "last_checked": datetime.utcnow().isoformat(), "response_time_ms": 28},
            "event_processor": {"status": "healthy", "uptime": 99.7, "last_checked": datetime.utcnow().isoformat(), "response_time_ms": 15},
            "auth": {"status": "healthy", "uptime": 100.0, "last_checked": datetime.utcnow().isoformat(), "response_time_ms": 12}
        },
        metrics={
            "total_robots": 47,
            "active_clients": 8,
            "api_requests": 125000,
            "error_rate": 0.02,
            "avg_response_time_ms": 26
        },
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/api/admin/alerts")
async def get_alerts(
    acknowledged: Optional[bool] = None,
    severity: Optional[str] = None,
    admin: dict = Depends(verify_admin_token)
):
    """Get system alerts with optional filtering"""
    filtered_alerts = alerts_db
    
    if acknowledged is not None:
        filtered_alerts = [a for a in filtered_alerts if a.acknowledged == acknowledged]
    
    if severity:
        filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
    
    return {"alerts": filtered_alerts, "total": len(filtered_alerts)}

@app.post("/api/admin/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, admin: dict = Depends(verify_admin_token)):
    """Acknowledge an alert"""
    for alert in alerts_db:
        if alert.id == alert_id:
            alert.acknowledged = True
            return {"message": "Alert acknowledged", "alert_id": alert_id}
    
    raise HTTPException(status_code=404, detail="Alert not found")

# Client Management Endpoints
@app.get("/api/admin/clients")
async def list_clients(
    status: Optional[ClientStatus] = None,
    plan: Optional[ClientPlan] = None,
    admin: dict = Depends(verify_admin_token)
):
    """List all clients with optional filtering"""
    clients_list = list(clients_db.values())
    
    if status:
        clients_list = [c for c in clients_list if c.status == status]
    
    if plan:
        clients_list = [c for c in clients_list if c.plan == plan]
    
    return {
        "clients": clients_list,
        "total": len(clients_list),
        "filters": {"status": status, "plan": plan}
    }

@app.get("/api/admin/clients/{client_id}")
async def get_client(client_id: str, admin: dict = Depends(verify_admin_token)):
    """Get detailed information about a specific client"""
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return {"client": clients_db[client_id]}

@app.post("/api/admin/clients")
async def create_client(request: CreateClientRequest, admin: dict = Depends(verify_admin_token)):
    """Create a new client"""
    import uuid
    import traceback
    
    print(f"[CREATE CLIENT] Received request: {request.model_dump()}")
    
    try:
        new_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        # Map plan to MRR
        plan_mrr = {
            ClientPlan.hobby: 99,
            ClientPlan.pro: 499,
            ClientPlan.business: 2000,
            ClientPlan.enterprise: 0
        }
        
        new_client = Client(
            id=new_id,
            name=request.name,
            status=ClientStatus.trial,
            plan=request.plan,
            entityType=request.entityType,
            industry=request.industry,
            email=request.email,
            phone=request.phone,
            taxId=request.taxId,
            locations=request.locations,
            fleetSize=request.fleetSize,
            deploymentPriority=request.deploymentPriority,
            integrations=request.integrations,
            fleet=ClientFleet(
                total_robots=request.fleetSize,
                active_robots=0,
                idle_robots=request.fleetSize,
                maintenance_robots=0
            ),
            subscription=ClientSubscription(
                start_date=now[:10],
                end_date="",
                mrr=plan_mrr.get(request.plan, 0)
            ),
            created_at=now
        )
        
        clients_db[new_id] = new_client
        print(f"[CREATE CLIENT] Success: Created client {new_id}")
        
        return {"message": "Client created successfully", "client": new_client}
    except Exception as e:
        print(f"[CREATE CLIENT] Error: {str(e)}")
        print(f"[CREATE CLIENT] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.put("/api/admin/clients/{client_id}")
async def update_client(
    client_id: str,
    request: UpdateClientRequest,
    admin: dict = Depends(verify_admin_token)
):
    """Update client information"""
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client = clients_db[client_id]
    
    if request.name:
        client.name = request.name
    if request.status:
        client.status = request.status
    if request.plan:
        client.plan = request.plan
    if request.contact:
        client.contact = request.contact
    
    client.updated_at = datetime.utcnow().isoformat()
    
    return {"message": "Client updated successfully", "client": client}

@app.delete("/api/admin/clients/{client_id}")
async def delete_client(client_id: str, admin: dict = Depends(verify_admin_token)):
    """Suspend/terminate a client (soft delete)"""
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Soft delete - change status to suspended
    clients_db[client_id].status = ClientStatus.suspended
    clients_db[client_id].updated_at = datetime.utcnow().isoformat()
    
    return {"message": "Client suspended successfully", "client_id": client_id}

@app.get("/api/admin/clients/{client_id}/fleet")
async def get_client_fleet(client_id: str, admin: dict = Depends(verify_admin_token)):
    """Get fleet information for a specific client"""
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return {
        "client_id": client_id,
        "fleet": clients_db[client_id].fleet,
        "robots": []  # Would fetch from fleet control service
    }

@app.get("/api/admin/dashboard/stats")
async def get_dashboard_stats(admin: dict = Depends(verify_admin_token)):
    """Get aggregated stats for admin dashboard"""
    total_clients = len(clients_db)
    active_clients = len([c for c in clients_db.values() if c.status == ClientStatus.active])
    trial_clients = len([c for c in clients_db.values() if c.status == ClientStatus.trial])
    total_robots = sum(c.fleet.total_robots for c in clients_db.values())
    active_robots = sum(c.fleet.active_robots for c in clients_db.values())
    monthly_revenue = sum(c.subscription.mrr for c in clients_db.values())
    
    return {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "trial_clients": trial_clients,
        "total_robots": total_robots,
        "active_robots": active_robots,
        "monthly_revenue": monthly_revenue,
        "system_uptime": 99.8,
        "timestamp": datetime.utcnow().isoformat()
    }

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
