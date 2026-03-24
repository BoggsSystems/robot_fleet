# 🗄️ Fleet Platform Data Layer Overview

## 🏗️ **Data Architecture Overview**

The fleet platform uses a **multi-layered data architecture** with SQLite persistence, real-time streaming, and distributed caching.

## 📊 **Core Data Components**

### **1. Persistent Storage Layer** (`ShadowWorldStore`)

#### **Database Schema**
```sql
-- Core Entity Tables
CREATE TABLE canonical_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    robot_id TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    topic TEXT,
    event_json TEXT NOT NULL
);

CREATE TABLE robot_state (
    robot_id TEXT PRIMARY KEY,
    fleet_id TEXT NOT NULL,
    site_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    state_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Fleet Organization
CREATE TABLE fleets (
    fleet_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE sites (
    site_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE zones (
    zone_id TEXT PRIMARY KEY,
    site_id TEXT NOT NULL,
    name TEXT NOT NULL,
    parent_zone_id TEXT,
    zone_type TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Robot Registry
CREATE TABLE robots (
    robot_id TEXT PRIMARY KEY,
    fleet_id TEXT NOT NULL,
    site_id TEXT NOT NULL,
    zone_id TEXT,
    name TEXT NOT NULL,
    status TEXT NOT NULL,
    ip_address TEXT NOT NULL,
    network_interface TEXT NOT NULL,
    model TEXT NOT NULL,
    serial TEXT NOT NULL,
    firmware TEXT NOT NULL,
    robot_type TEXT NOT NULL,
    robot_category TEXT NOT NULL,
    vendor TEXT NOT NULL,
    capabilities_json TEXT NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Task Management
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    robot_id TEXT,
    fleet_id TEXT NOT NULL,
    site_id TEXT NOT NULL,
    zone_id TEXT,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL,
    spec_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Command Queue
CREATE TABLE commands (
    command_id TEXT PRIMARY KEY,
    robot_id TEXT NOT NULL,
    command_type TEXT NOT NULL,
    status TEXT NOT NULL,
    parameters_json TEXT NOT NULL,
    issued_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Onboarding & Mission Management
CREATE TABLE onboarding_records (
    robot_id TEXT PRIMARY KEY,
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    details_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE mission_sessions (
    mission_id TEXT PRIMARY KEY,
    request_text TEXT NOT NULL,
    requested_by TEXT NOT NULL,
    status TEXT NOT NULL,
    preview_json TEXT NOT NULL,
    question_json TEXT NOT NULL,
    request_json TEXT NOT NULL DEFAULT '{}',
    proposal_json TEXT NOT NULL DEFAULT '{}',
    validated_plan_json TEXT NOT NULL DEFAULT '{}',
    approval_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

#### **Data Flow Architecture**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   iOS Frontend  │───▶│   REST API      │───▶│  Fleet Backend  │
│   (Swift)       │    │   (FastAPI)     │    │  (Services)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Event Stream   │    │  ShadowWorld    │
                       │  (WebSocket)     │    │  Store (SQLite) │
                       └──────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Real-time UI   │    │  Vector DB      │
                       │  Updates         │    │  (RAG System)   │
                       └──────────────────┘    └─────────────────┘
```

### **2. Service Layer** (`FleetBackendServices`)

#### **Service Architecture**
```python
@dataclass
class FleetBackendServices:
    """Service layer for persistent fleet backend entities."""
    
    store: ShadowWorldStore          # SQLite persistence
    config: LocalRuntimeConfig       # Runtime configuration
    
    # Service Methods:
    # - Fleet management (create, list, update fleets)
    # - Robot registry (register, list, update robots)
    # - Task management (create, assign, track tasks)
    # - Command queue (issue, track, execute commands)
    # - Onboarding (stage, progress, completion)
    # - Mission sessions (create, manage, complete missions)
```

#### **Service Integration**
```python
# Example service method
def list_robots(self, fleet_id: str | None = None) -> list[dict]:
    """List robots with optional fleet filtering."""
    records = self.store.list_robot_records()
    
    if fleet_id:
        records = [r for r in records if r["fleet_id"] == fleet_id]
    
    # Deserialize JSON fields
    robots = []
    for record in records:
        robot = dict(record)
        robot["capabilities"] = json.loads(robot["capabilities_json"])
        robot["metadata"] = json.loads(robot["metadata_json"])
        robots.append(robot)
    
    return robots
```

### **3. iOS Data Layer** (Swift)

#### **Domain Models** (`RobotModels.swift`)
```swift
// Core Data Models
struct RobotConfig: Codable, Identifiable {
    let id: String
    let robotId: String
    let name: String
    let ipAddress: String
    let networkInterface: String
    let capabilities: [String]
    let robotType: String
    let robotCategory: String
    let vendor: String
    let model: String
    let serial: String
    let firmware: String
    let zone: String?
    let subZone: String?
    let status: String
    let batteryLevel: Double?
    let payloadCapacityKg: Double?
    let metadata: [String: Any]
}

// Response Models
struct RobotRegistrationResponse: Codable {
    let robot: RobotConfig
    let onboarding: OnboardingStatus
}

struct OnboardingStatus: Codable {
    let stage: String
    let status: String
    let progress: Double
    let estimatedTimeRemaining: Int?
    let currentStep: String
    let nextStep: String?
}
```

#### **Service Layer** (`RobotService.swift`)
```swift
// Service Protocol
protocol RobotServiceProtocol {
    func listRobots(fleetId: String?) async throws -> RobotListResponse
    func registerRobot(config: RobotConfig) async throws -> RobotRegistrationResponse
    func updateRobotStatus(robotId: String, update: RobotStatusUpdate) async throws -> RobotConfig
    func removeRobot(robotId: String) async throws
    func testConnection(config: RobotConfig) async throws -> RobotConnectionResponse
    func calibrateRobot(robotId: String, request: CalibrationRequest) async throws -> CalibrationResponse
}

// Live Implementation
class RobotServiceLive: RobotServiceProtocol {
    private let apiClient: APIClient
    
    func listRobots(fleetId: String? = nil) async throws -> RobotListResponse {
        let endpoint = "/api/robots"
        let parameters = fleetId.map { ["fleet_id": $0] } ?? [:]
        
        let response: RobotListResponse = try await apiClient.get(
            endpoint: endpoint,
            parameters: parameters
        )
        
        return response
    }
}
```

#### **ViewModel Layer** (`RobotViewModel.swift`)
```swift
@MainActor
class RobotViewModel: ObservableObject {
    @Published var robots: [RobotConfig] = []
    @Published var isLoading = false
    @Published var error: String?
    @Published var registrationConfig = RobotConfig.empty
    @Published var connectionTestResult: RobotConnectionResponse?
    @Published var isRegistering = false
    @Published var isTestingConnection = false
    
    // Data Operations
    func loadRobots(fleetId: String? = nil) async {
        await MainActor.run {
            isLoading = true
            error = nil
        }
        
        do {
            let response = try await robotService.listRobots(fleetId: fleetId)
            await MainActor.run {
                self.robots = response.robots.sorted { $0.name < $1.name }
                isLoading = false
            }
        } catch {
            await MainActor.run {
                self.error = "Failed to load robots: \(error.localizedDescription)"
                isLoading = false
            }
        }
    }
}
```

### **4. RAG Data Layer** (Vector Database)

#### **Vector Storage Schema**
```sql
-- RAG Documents Table
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    metadata TEXT NOT NULL,
    client_id TEXT NOT NULL,
    scope TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    access_count INTEGER DEFAULT 0,
    effectiveness_score REAL DEFAULT 1.0,
    embedding BLOB
);

-- Client Registry
CREATE TABLE clients (
    client_id TEXT PRIMARY KEY,
    config TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_activity TEXT NOT NULL,
    query_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0
);
```

#### **Multi-Tenant Structure**
```
data/rag/
├── shared_knowledge.db              # Common knowledge (robots, missions, safety)
├── clients/
│   ├── cot_12345678/               # Cottage client
│   │   ├── cot_12345678.db          # Client-specific database
│   │   ├── personal/                # User interactions & learning
│   │   ├── layouts/                 # Cottage floor plans
│   │   └── history/                 # Query history & patterns
│   ├── com_12345678/               # Commercial client
│   └── ind_12345678/               # Industrial client
└── indexes/                         # Vector embeddings for search
```

## 🔄 **Data Flow Patterns**

### **1. Robot Registration Flow**
```
1. iOS App → POST /api/robots/register
2. FastAPI → FleetBackendServices.register_robot()
3. Services → ShadowWorldStore.add_robot()
4. Store → INSERT INTO robots table
5. Store → INSERT INTO onboarding_records
6. Response → iOS App with robot config
7. iOS App → Update UI with new robot
```

### **2. Mission Creation Flow**
```
1. iOS App → POST /api/mobile/missions/preview
2. FastAPI → MissionBrain.preview_mission()
3. Brain → RAG search for contextual knowledge
4. RAG → Vector similarity search
5. Brain → AI intent parsing with context
6. Brain → Task generation and assignment
7. Response → iOS App with mission plan
8. iOS App → User confirmation
9. iOS App → POST /api/mobile/missions/{id}/dispatch
10. FastAPI → FleetController.dispatch_mission()
11. Controller → DynamicTaskExecutor.execute_task()
12. Executor → Robot SDK → Physical robot
```

### **3. Real-time Updates Flow**
```
1. Robot SDK → Task completion event
2. SDK → WebSocket → FleetController
3. Controller → ShadowWorldStore.update_task()
4. Store → UPDATE tasks table
5. Store → INSERT canonical_events
6. WebSocket → Broadcast to all clients
7. iOS App → Receive WebSocket update
8. iOS App → Update UI in real-time
```

## 📊 **Data Relationships**

### **Entity Relationships**
```
Fleets (1:N) Sites (1:N) Zones (1:N) Robots
  ↓           ↓         ↓        ↓
Missions → Tasks → Commands → Events
  ↓           ↓         ↓
Onboarding → Status → State
```

### **Data Consistency**
```python
# Transaction example for robot registration
def register_robot_transaction(robot_config: RobotConfig):
    with store.transaction():
        # 1. Add robot to registry
        store.add_robot(robot_config)
        
        # 2. Initialize onboarding
        store.add_onboarding_record(robot_config.robot_id, "discovery")
        
        # 3. Create initial state
        store.update_robot_state(robot_config.robot_id, initial_state)
        
        # 4. Log canonical event
        store.add_canonical_event(
            event_type="robot_registered",
            robot_id=robot_config.robot_id,
            event_data={"config": robot_config.dict()}
        )
        
        # 5. Update fleet metrics
        store.update_fleet_metrics(robot_config.fleet_id)
```

## 🔧 **Data Management Features**

### **1. Caching Strategy**
```python
class DataCache:
    def __init__(self):
        self.robot_cache = {}           # robot_id → RobotConfig
        self.fleet_cache = {}           # fleet_id → FleetInfo
        self.zone_cache = {}            # zone_id → ZoneInfo
        self.task_cache = {}            # task_id → TaskInfo
        
    def get_robot(self, robot_id: str) -> Optional[RobotConfig]:
        if robot_id not in self.robot_cache:
            robot = self.store.get_robot(robot_id)
            if robot:
                self.robot_cache[robot_id] = robot
        return self.robot_cache.get(robot_id)
```

### **2. Event Sourcing**
```python
# All state changes are recorded as canonical events
class CanonicalEvent:
    event_id: str
    event_type: str
    robot_id: str
    occurred_at: str
    topic: str
    event_json: str

# Event Types:
# - robot_registered
# - robot_status_changed
# - task_created
# - task_started
# - task_completed
# - command_issued
# - command_executed
```

### **3. Data Migration**
```python
class DataMigration:
    def migrate_v1_to_v2(self):
        """Migrate from v1 to v2 schema"""
        with self.store.transaction():
            # Add new columns
            self.store.add_column("robots", "tenant_id", "TEXT")
            self.store.add_column("robots", "zone_id", "TEXT")
            
            # Migrate existing data
            for robot in self.store.list_robots():
                robot["tenant_id"] = "default"
                robot["zone_id"] = robot.get("metadata", {}).get("zone")
                self.store.update_robot(robot)
```

## 📈 **Performance Optimization**

### **1. Database Indexing**
```sql
-- Optimized indexes for common queries
CREATE INDEX idx_robots_fleet_id ON robots(fleet_id);
CREATE INDEX idx_robots_site_id ON robots(site_id);
CREATE INDEX idx_robots_zone_id ON robots(zone_id);
CREATE INDEX idx_robots_status ON robots(status);
CREATE INDEX idx_tasks_robot_id ON tasks(robot_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_events_robot_id ON canonical_events(robot_id);
CREATE INDEX idx_events_occurred_at ON canonical_events(occurred_at);
```

### **2. Connection Pooling**
```python
class DatabasePool:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = asyncio.Queue(maxsize=max_connections)
        self.semaphore = asyncio.Semaphore(max_connections)
    
    async def get_connection(self):
        await self.semaphore.acquire()
        try:
            return await self.connections.get()
        except asyncio.QueueEmpty:
            return sqlite3.connect(self.db_path)
    
    async def return_connection(self, conn):
        await self.connections.put(conn)
        self.semaphore.release()
```

### **3. Batch Operations**
```python
def batch_update_robot_states(updates: List[RobotStateUpdate]):
    """Update multiple robot states in a single transaction"""
    with store.transaction():
        for update in updates:
            store.update_robot_state(update.robot_id, update.state)
            store.add_canonical_event(
                event_type="robot_state_changed",
                robot_id=update.robot_id,
                event_data=update.state
            )
```

## 🎯 **Data Layer Benefits**

### **Reliability**
- **ACID Transactions**: Ensure data consistency
- **Event Sourcing**: Complete audit trail
- **Backup & Recovery**: SQLite backup strategies
- **Data Validation**: Type safety and constraints

### **Scalability**
- **Multi-Tenant**: Support multiple clients
- **Horizontal Scaling**: Database sharding capability
- **Caching**: Multiple caching layers
- **Connection Pooling**: Efficient resource usage

### **Real-time**
- **WebSocket Streaming**: Live updates
- **Event-Driven**: Reactive architecture
- **Optimistic Updates**: Fast UI responsiveness
- **Conflict Resolution**: Handle concurrent updates

The data layer provides a **robust, scalable, and real-time** foundation for the entire fleet management platform!
