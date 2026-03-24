"""
Dynamic robot fleet management system with database persistence.
"""

from __future__ import annotations

import asyncio
import json
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import aiosqlite


@dataclass
class Robot:
    """Robot fleet entity"""
    robot_id: str
    fleet_id: str
    site_id: str
    zone_id: Optional[str]
    name: str
    status: str  # available, busy, charging, maintenance, offline
    ip_address: str
    network_interface: str
    model: str
    serial: str
    firmware: str
    robot_type: str
    robot_category: str
    capabilities_json: str
    metadata_json: str
    created_at: str
    updated_at: str


@dataclass
class RobotState:
    """Real-time robot state"""
    robot_id: str
    fleet_id: str
    site_id: str
    tenant_id: str
    state_json: str
    updated_at: str


@dataclass
class RobotRegistration:
    """Robot registration request"""
    fleet_id: str
    site_id: str
    tenant_id: str
    name: str
    robot_type: str
    robot_category: str
    ip_address: str
    network_interface: str
    model: str
    serial: str
    firmware: str
    capabilities: List[str]
    metadata: Dict[str, Any]


class RobotFleetManager:
    """Dynamic robot fleet management"""
    
    def __init__(self, db_path: str = "data/fleet.db"):
        self.db_path = db_path
        self.db = None
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize fleet database"""
        await self._create_tables()
        await self._seed_default_fleet()
    
    async def _create_tables(self):
        """Create fleet management tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Robots table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS robots (
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
                    capabilities_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Robot state table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS robot_state (
                    robot_id TEXT PRIMARY KEY,
                    fleet_id TEXT NOT NULL,
                    site_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Fleet status view
            await db.execute("""
                CREATE VIEW IF NOT EXISTS fleet_status AS
                SELECT 
                    fleet_id,
                    site_id,
                    COUNT(CASE WHEN status = 'available' THEN 1 END) as available_count,
                    COUNT(CASE WHEN status = 'busy' THEN 1 END) as busy_count,
                    COUNT(CASE WHEN status = 'charging' THEN 1 END) as charging_count,
                    COUNT(CASE WHEN status = 'maintenance' THEN 1 END) as maintenance_count,
                    COUNT(*) as total_count
                FROM robots
                GROUP BY fleet_id, site_id
            """)
            
            await db.commit()
    
    async def _seed_default_fleet(self):
        """Seed with default cottage fleet"""
        default_robots = [
            {
                "robot_type": "quadruped",
                "robot_category": "ground",
                "name": "Quadruped Explorer",
                "model": "QT-001",
                "serial": "QT-001-2024-001",
                "firmware": "v2.1.0",
                "ip_address": "192.168.1.101",
                "network_interface": "WiFi",
                "capabilities": ["outdoor_navigation", "rough_terrain_handling", "payload_transport", "qr_scanning", "patrol"],
                "metadata": {"manufacturer": "RobotiCorp", "year": 2024, "weight_kg": 45.0}
            },
            {
                "robot_type": "humanoid",
                "robot_category": "ground", 
                "name": "Humanoid Assistant",
                "model": "HA-001",
                "serial": "HA-001-2024-001",
                "firmware": "v1.8.0",
                "ip_address": "192.168.1.102",
                "network_interface": "WiFi",
                "capabilities": ["fine_manipulation", "object_recognition", "qr_scanning", "cleaning", "assistance"],
                "metadata": {"manufacturer": "HumanoidTech", "year": 2024, "height_cm": 165, "weight_kg": 35.0}
            },
            {
                "robot_type": "drone",
                "robot_category": "aerial",
                "name": "Aerial Scout",
                "model": "AS-001", 
                "serial": "AS-001-2024-001",
                "firmware": "v3.0.0",
                "ip_address": "192.168.1.103",
                "network_interface": "WiFi",
                "capabilities": ["aerial_surveillance", "qr_scanning", "photography", "inspection", "delivery"],
                "metadata": {"manufacturer": "DroneTech", "year": 2024, "flight_time_min": 30, "max_payload_kg": 2.0}
            }
        ]
        
        for i, robot_data in enumerate(default_robots):
            robot_id = f"{robot_data['robot_type'][:4].lower()}_{i+1:03d}"
            
            robot = Robot(
                robot_id=robot_id,
                fleet_id="cottage_fleet",
                site_id="cottage_main",
                zone_id="charging_station",
                name=robot_data["name"],
                status="available",
                ip_address=robot_data["ip_address"],
                network_interface=robot_data["network_interface"],
                model=robot_data["model"],
                serial=robot_data["serial"],
                firmware=robot_data["firmware"],
                robot_type=robot_data["robot_type"],
                robot_category=robot_data["robot_category"],
                capabilities_json=json.dumps(robot_data["capabilities"]),
                metadata_json=json.dumps(robot_data["metadata"]),
                created_at=datetime.now(timezone.utc).isoformat(),
                updated_at=datetime.now(timezone.utc).isoformat()
            )
            
            await self.create_robot(robot)
            
            # Create initial state
            state = RobotState(
                robot_id=robot_id,
                fleet_id="cottage_fleet",
                site_id="cottage_main",
                tenant_id="cot_12345678",
                state_json=json.dumps({
                    "battery_level": 100.0,
                    "current_location": "charging_station",
                    "current_task": None,
                    "last_mission": None,
                    "maintenance_status": "good",
                    "sensor_data": {},
                    "health_status": "optimal"
                }),
                updated_at=datetime.now(timezone.utc).isoformat()
            )
            
            await self.create_robot_state(state)
        
        print(f"✅ Seeded default fleet with {len(default_robots)} robots")
    
    async def register_robot(self, registration: RobotRegistration) -> Robot:
        """Register new robot in fleet"""
        async with self._lock:
            # Generate unique robot ID
            robot_id = f"{registration.robot_type[:4].lower()}_{random.randint(100, 999):03d}"
            
            robot = Robot(
                robot_id=robot_id,
                fleet_id=registration.fleet_id,
                site_id=registration.site_id,
                zone_id=None,
                name=registration.name,
                status="available",
                ip_address=registration.ip_address,
                network_interface=registration.network_interface,
                model=registration.model,
                serial=registration.serial,
                firmware=registration.firmware,
                robot_type=registration.robot_type,
                robot_category=registration.robot_category,
                capabilities_json=json.dumps(registration.capabilities),
                metadata_json=json.dumps(registration.metadata),
                created_at=datetime.now(timezone.utc).isoformat(),
                updated_at=datetime.now(timezone.utc).isoformat()
            )
            
            await self.create_robot(robot)
            
            # Create initial state
            state = RobotState(
                robot_id=robot_id,
                fleet_id=registration.fleet_id,
                site_id=registration.site_id,
                tenant_id=registration.tenant_id,
                state_json=json.dumps({
                    "battery_level": 100.0,
                    "current_location": "charging_station",
                    "current_task": None,
                    "last_mission": None,
                    "maintenance_status": "good",
                    "sensor_data": {},
                    "health_status": "optimal"
                }),
                updated_at=datetime.now(timezone.utc).isoformat()
            )
            
            await self.create_robot_state(state)
            
            print(f"✅ Registered robot {robot_id}: {registration.name}")
            return robot
    
    async def create_robot(self, robot: Robot):
        """Create robot record"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO robots (
                    robot_id, fleet_id, site_id, zone_id, name, status, ip_address,
                    network_interface, model, serial, firmware, robot_type, robot_category,
                    capabilities_json, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                robot.robot_id, robot.fleet_id, robot.site_id, robot.zone_id, robot.name,
                robot.status, robot.ip_address, robot.network_interface, robot.model,
                robot.serial, robot.firmware, robot.robot_type, robot.robot_category,
                robot.capabilities_json, robot.metadata_json, robot.created_at, robot.updated_at
            ))
            await db.commit()
    
    async def create_robot_state(self, state: RobotState):
        """Create robot state record"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO robot_state (
                    robot_id, fleet_id, site_id, tenant_id, state_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                state.robot_id, state.fleet_id, state.site_id, state.tenant_id,
                state.state_json, state.updated_at
            ))
            await db.commit()
    
    async def get_robots_by_fleet(self, fleet_id: str) -> List[Robot]:
        """Get all robots in a fleet"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM robots WHERE fleet_id = ? ORDER BY created_at
            """, (fleet_id,))
            
            rows = await cursor.fetchall()
            return [Robot(**row) for row in rows]
    
    async def get_robot_states_by_fleet(self, fleet_id: str) -> Dict[str, RobotState]:
        """Get all robot states in a fleet"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM robot_state WHERE fleet_id = ?
            """, (fleet_id,))
            
            rows = await cursor.fetchall()
            return {row["robot_id"]: RobotState(**row) for row in rows}
    
    async def get_fleet_status(self, fleet_id: str) -> Dict[str, Any]:
        """Get fleet status summary"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM fleet_status WHERE fleet_id = ?
            """, (fleet_id,))
            
            row = await cursor.fetchone()
            return dict(row) if row else {}
    
    async def update_robot_status(self, robot_id: str, status: str, zone_id: Optional[str] = None):
        """Update robot status"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE robots SET status = ?, zone_id = ?, updated_at = ? WHERE robot_id = ?
            """, (status, zone_id, datetime.now(timezone.utc).isoformat(), robot_id))
            await db.commit()
    
    async def update_robot_state(self, robot_id: str, state_updates: Dict[str, Any]):
        """Update robot state"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get current state
            cursor = await db.execute("""
                SELECT state_json FROM robot_state WHERE robot_id = ?
            """, (robot_id,))
            row = await cursor.fetchone()
            
            if row:
                current_state = json.loads(row["state_json"])
                current_state.update(state_updates)
                
                await db.execute("""
                    UPDATE robot_state SET state_json = ?, updated_at = ? WHERE robot_id = ?
                """, (
                    json.dumps(current_state),
                    datetime.now(timezone.utc).isoformat(),
                    robot_id
                ))
                await db.commit()
    
    async def get_available_robots(self, fleet_id: str) -> List[Robot]:
        """Get available robots in fleet"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM robots WHERE fleet_id = ? AND status = 'available'
            """, (fleet_id,))
            
            rows = await cursor.fetchall()
            return [Robot(**row) for row in rows]
    
    async def get_robot_by_id(self, robot_id: str) -> Optional[Robot]:
        """Get robot by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM robots WHERE robot_id = ?
            """, (robot_id,))
            
            row = await cursor.fetchone()
            return Robot(**row) if row else None
    
    async def delete_robot(self, robot_id: str):
        """Delete robot from fleet"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM robots WHERE robot_id = ?", (robot_id,))
            await db.execute("DELETE FROM robot_state WHERE robot_id = ?", (robot_id,))
            await db.commit()
            print(f"🗑️ Deleted robot {robot_id} from fleet")


# Fleet context provider for RAG integration
class FleetContextProvider:
    """Provide real-time fleet context for RAG system"""
    
    def __init__(self, fleet_manager: RobotFleetManager):
        self.fleet_manager = fleet_manager
    
    async def get_fleet_context(self, fleet_id: str) -> Dict[str, Any]:
        """Get comprehensive fleet context"""
        
        # Get robots and states
        robots = await self.fleet_manager.get_robots_by_fleet(fleet_id)
        robot_states = await self.fleet_manager.get_robot_states_by_fleet(fleet_id)
        
        # Build context
        context = {
            "robots": {},
            "available_robots": [],
            "busy_robots": [],
            "charging_robots": [],
            "maintenance_robots": [],
            "offline_robots": [],
            "fleet_status": await self.fleet_manager.get_fleet_status(fleet_id)
        }
        
        for robot in robots:
            robot_id = robot.robot_id
            state = robot_states.get(robot_id)
            
            robot_info = {
                "id": robot_id,
                "name": robot.name,
                "type": robot.robot_type,
                "category": robot.robot_category,
                "capabilities": json.loads(robot.capabilities_json),
                "status": robot.status,
                "ip_address": robot.ip_address,
                "model": robot.model,
                "metadata": json.loads(robot.metadata_json)
            }
            
            if state:
                state_data = json.loads(state.state_json)
                robot_info.update({
                    "battery_level": state_data.get("battery_level", 0),
                    "current_location": state_data.get("current_location", "unknown"),
                    "current_task": state_data.get("current_task"),
                    "last_mission": state_data.get("last_mission"),
                    "maintenance_status": state_data.get("maintenance_status", "unknown"),
                    "health_status": state_data.get("health_status", "unknown"),
                    "sensor_data": state_data.get("sensor_data", {})
                })
            
            context["robots"][robot_id] = robot_info
            
            # Categorize by status
            if robot.status == "available":
                context["available_robots"].append(robot_info)
            elif robot.status == "busy":
                context["busy_robots"].append(robot_info)
            elif robot.status == "charging":
                context["charging_robots"].append(robot_info)
            elif robot.status == "maintenance":
                context["maintenance_robots"].append(robot_info)
            else:
                context["offline_robots"].append(robot_info)
        
        return context
    
    async def update_robot_from_rag_context(self, robot_id: str, context_updates: Dict[str, Any]):
        """Update robot based on RAG context"""
        
        # Extract relevant updates
        state_updates = {}
        
        if "battery_level" in context_updates:
            state_updates["battery_level"] = context_updates["battery_level"]
        
        if "current_location" in context_updates:
            state_updates["current_location"] = context_updates["current_location"]
        
        if "current_task" in context_updates:
            state_updates["current_task"] = context_updates["current_task"]
        
        if "status" in context_updates:
            await self.fleet_manager.update_robot_status(
                robot_id, 
                context_updates["status"],
                context_updates.get("zone_id")
            )
        
        if state_updates:
            await self.fleet_manager.update_robot_state(robot_id, state_updates)


# Initialize fleet manager
fleet_manager = RobotFleetManager()
fleet_context_provider = FleetContextProvider(fleet_manager)


# Setup function
async def setup_fleet_database():
    """Setup the fleet database"""
    await fleet_manager.initialize()
    print("🚀 Fleet database initialized with dynamic robot management")
