#!/usr/bin/env python3
"""
Robot Fleet Configuration API
Provides endpoints for robot types and fleet configuration
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import sqlite3
from datetime import datetime

# Import the database seeder
from robot_database_seeder import RobotDatabaseSeeder

router = APIRouter(prefix="/api/robots", tags=["robots"])

# Pydantic models for API responses
class RobotCapability(BaseModel):
    name: str
    description: str

class RobotSpecification(BaseModel):
    weight_capacity: float
    battery_life_hours: float
    max_speed_kmh: float
    navigation_system: str
    sensor_suite: List[str]
    dimensions: Dict[str, float]
    weight_kg: float
    operating_temperature_range: str
    ip_rating: str
    connectivity_options: List[str]

class RobotType(BaseModel):
    id: str
    manufacturer: str
    model: str
    robot_type: str
    capabilities: List[str]
    specifications: RobotSpecification
    weight_capacity: float
    battery_life_hours: float
    max_speed_kmh: float
    navigation_system: str
    price_amount: float
    availability_status: str
    image_url: Optional[str] = None
    documentation_url: Optional[str] = None
    data_sheet_url: Optional[str] = None

class RobotFilter(BaseModel):
    robot_type: Optional[str] = None
    manufacturer: Optional[str] = None
    min_payload: Optional[float] = None
    max_price: Optional[float] = None
    environment: Optional[str] = None  # 'indoor', 'outdoor', 'mixed'

class FleetRobotRequest(BaseModel):
    robot_id: str
    quantity: int
    custom_name: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None

# Database connection
def get_db_connection():
    """Get database connection"""
    return sqlite3.connect("data/robot_fleet.db")

@router.get("/types", response_model=List[RobotType])
async def get_robot_types(
    robot_type: Optional[str] = Query(None, description="Filter by robot type"),
    manufacturer: Optional[str] = Query(None, description="Filter by manufacturer"),
    min_payload: Optional[float] = Query(None, description="Minimum payload capacity in kg"),
    max_price: Optional[float] = Query(None, description="Maximum price in USD"),
    available_only: bool = Query(True, description="Only show available robots")
):
    """
    Get all available robot types for fleet configuration
    """
    try:
        seeder = RobotDatabaseSeeder()
        seeder.connect()
        
        # Build filters
        filters = {}
        if robot_type:
            filters["robot_type"] = robot_type
        if manufacturer:
            filters["manufacturer"] = manufacturer
        if min_payload:
            filters["min_payload"] = min_payload
        if max_price:
            filters["max_price"] = max_price
            
        robots_data = seeder.search_robots(filters)
        
        # Convert to response models
        robots = []
        for robot in robots_data:
            if available_only and robot["availability_status"] != "available":
                continue
                
            robot_spec = RobotSpecification(**robot["specifications"])
            robot_response = RobotType(
                id=robot["id"],
                manufacturer=robot["manufacturer"],
                model=robot["model"],
                robot_type=robot["robot_type"],
                capabilities=robot["capabilities"],
                specifications=robot_spec,
                weight_capacity=robot["weight_capacity"],
                battery_life_hours=robot["battery_life_hours"],
                max_speed_kmh=robot["max_speed_kmh"],
                navigation_system=robot["navigation_system"],
                price_amount=robot["price_amount"],
                availability_status=robot["availability_status"],
                image_url=robot.get("image_url"),
                documentation_url=robot.get("documentation_url"),
                data_sheet_url=robot.get("data_sheet_url")
            )
            robots.append(robot_response)
            
        seeder.close()
        return robots
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching robot types: {str(e)}")

@router.get("/types/{robot_id}", response_model=RobotType)
async def get_robot_type_by_id(robot_id: str):
    """
    Get detailed information about a specific robot type
    """
    try:
        seeder = RobotDatabaseSeeder()
        seeder.connect()
        
        robot_data = seeder.get_robot_by_id(robot_id)
        if not robot_data:
            raise HTTPException(status_code=404, detail="Robot not found")
            
        robot_spec = RobotSpecification(**robot_data["specifications"])
        robot_response = RobotType(
            id=robot_data["id"],
            manufacturer=robot_data["manufacturer"],
            model=robot_data["model"],
            robot_type=robot_data["robot_type"],
            capabilities=robot_data["capabilities"],
            specifications=robot_spec,
            weight_capacity=robot_data["weight_capacity"],
            battery_life_hours=robot_data["battery_life_hours"],
            max_speed_kmh=robot_data["max_speed_kmh"],
            navigation_system=robot_data["navigation_system"],
            price_amount=robot_data["price_amount"],
            availability_status=robot_data["availability_status"],
            image_url=robot_data.get("image_url"),
            documentation_url=robot_data.get("documentation_url"),
            data_sheet_url=robot_data.get("data_sheet_url")
        )
        
        seeder.close()
        return robot_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching robot type: {str(e)}")

@router.get("/manufacturers")
async def get_manufacturers():
    """
    Get all robot manufacturers
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT manufacturer, COUNT(*) as robot_count
            FROM robot_types 
            WHERE availability_status = 'available'
            GROUP BY manufacturer
            ORDER BY manufacturer
        """)
        
        manufacturers = []
        for row in cursor.fetchall():
            manufacturers.append({
                "name": row[0],
                "robot_count": row[1]
            })
            
        conn.close()
        return manufacturers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching manufacturers: {str(e)}")

@router.get("/capabilities")
async def get_capabilities():
    """
    Get all available robot capabilities
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT capabilities
            FROM robot_types 
            WHERE availability_status = 'available'
        """)
        
        all_capabilities = set()
        for row in cursor.fetchall():
            capabilities = json.loads(row[0])
            all_capabilities.update(capabilities)
            
        conn.close()
        
        # Format capabilities with descriptions
        capability_descriptions = {
            "package_delivery": "Deliver packages and goods",
            "navigation": "Autonomous navigation and path planning",
            "obstacle_avoidance": "Detect and avoid obstacles",
            "climbing": "Climb stairs and obstacles",
            "dynamic_balance": "Maintain balance during movement",
            "surveillance": "Monitor and patrol areas",
            "patrol": "Autonomous patrol routes",
            "alert_system": "Send alerts and notifications",
            "human_detection": "Detect human presence",
            "night_vision": "Operate in low light conditions",
            "visual_inspection": "Visual inspection and monitoring",
            "sensor_monitoring": "Monitor environmental sensors",
            "reporting": "Generate inspection reports",
            "thermal_imaging": "Thermal camera imaging",
            "gas_detection": "Detect gas leaks and air quality",
            "diagnostics": "System diagnostics and health checks",
            "repair_assistance": "Assist with maintenance tasks",
            "preventive_maintenance": "Schedule preventive maintenance",
            "tool_carrying": "Carry tools and equipment",
            "remote_operation": "Remote control and operation"
        }
        
        capabilities_list = []
        for capability in sorted(all_capabilities):
            capabilities_list.append({
                "name": capability,
                "description": capability_descriptions.get(capability, f"Capability: {capability}")
            })
            
        return capabilities_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching capabilities: {str(e)}")

@router.post("/fleet/calculate")
async def calculate_fleet_requirements(robots: List[FleetRobotRequest]):
    """
    Calculate fleet requirements and recommendations
    """
    try:
        seeder = RobotDatabaseSeeder()
        seeder.connect()
        
        fleet_analysis = {
            "total_robots": len(robots),
            "total_cost": 0.0,
            "total_weight_capacity": 0.0,
            "battery_requirements": {},
            "space_requirements": {},
            "network_requirements": {},
            "compatibility_issues": [],
            "recommendations": []
        }
        
        robot_types = {}
        
        for robot_req in robots:
            robot_data = seeder.get_robot_by_id(robot_req.robot_id)
            if not robot_data:
                fleet_analysis["compatibility_issues"].append(f"Robot {robot_req.robot_id} not found")
                continue
                
            # Calculate totals
            robot_cost = robot_data["price_amount"] * robot_req.quantity
            fleet_analysis["total_cost"] += robot_cost
            
            robot_capacity = robot_data["weight_capacity"] * robot_req.quantity
            fleet_analysis["total_weight_capacity"] += robot_capacity
            
            # Group by robot type for analysis
            robot_type_key = f"{robot_data['manufacturer']}_{robot_data['model']}"
            if robot_type_key not in robot_types:
                robot_types[robot_type_key] = {
                    "data": robot_data,
                    "quantity": 0,
                    "total_cost": 0.0,
                    "total_capacity": 0.0
                }
                
            robot_types[robot_type_key]["quantity"] += robot_req.quantity
            robot_types[robot_type_key]["total_cost"] += robot_cost
            robot_types[robot_type_key]["total_capacity"] += robot_capacity
            
        seeder.close()
        
        # Generate recommendations
        fleet_analysis["robot_types"] = []
        for robot_type_key, robot_info in robot_types.items():
            fleet_analysis["robot_types"].append({
                "manufacturer": robot_info["data"]["manufacturer"],
                "model": robot_info["data"]["model"],
                "quantity": robot_info["quantity"],
                "total_cost": robot_info["total_cost"],
                "total_capacity": robot_info["total_capacity"],
                "capabilities": robot_info["data"]["capabilities"]
            })
            
        # Add recommendations
        if fleet_analysis["total_cost"] > 100000:
            fleet_analysis["recommendations"].append("Consider phased deployment to manage costs")
            
        if len(robot_types) > 3:
            fleet_analysis["recommendations"].append("Large fleet variety may increase maintenance complexity")
            
        if fleet_analysis["total_weight_capacity"] > 100:
            fleet_analysis["recommendations"].append("Consider specialized heavy-lift robots for better efficiency")
            
        return fleet_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating fleet requirements: {str(e)}")

@router.get("/compatibility/{robot_id}")
async def get_robot_compatibility(robot_id: str):
    """
    Get compatibility information for a specific robot
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rc.environment_type, rc.terrain_types, rc.weather_conditions,
                   rc.space_requirements, rc.power_requirements, rc.network_requirements,
                   rc.safety_features, rt.manufacturer, rt.model, rt.robot_type
            FROM robot_compatibility rc
            JOIN robot_types rt ON rc.robot_type_id = rt.id
            WHERE rc.robot_type_id = ?
        """, (robot_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Compatibility data not found")
            
        compatibility = {
            "robot_id": robot_id,
            "manufacturer": row[8],
            "model": row[9],
            "robot_type": row[10],
            "environment_type": row[0],
            "terrain_types": json.loads(row[1]),
            "weather_conditions": json.loads(row[2]),
            "space_requirements": json.loads(row[3]),
            "power_requirements": json.loads(row[4]),
            "network_requirements": json.loads(row[5]),
            "safety_features": json.loads(row[6])
        }
        
        conn.close()
        return compatibility
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching compatibility data: {str(e)}")

@router.post("/seed-database")
async def seed_robot_database():
    """
    Seed the database with robot data (for initial setup)
    """
    try:
        seeder = RobotDatabaseSeeder()
        seeder.connect()
        
        seeder.create_tables()
        manufacturer_id = seeder.seed_manufacturers()
        seeder.seed_robot_types(manufacturer_id)
        
        seeder.close()
        
        return {
            "message": "Database seeded successfully",
            "manufacturer_id": manufacturer_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error seeding database: {str(e)}")

# Initialize the database on startup
@router.on_event("startup")
async def startup_event():
    """Initialize robot database on startup"""
    try:
        seeder = RobotDatabaseSeeder()
        seeder.connect()
        seeder.create_tables()
        
        # Check if we have any data
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM robot_types")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            # Seed initial data
            manufacturer_id = seeder.seed_manufacturers()
            seeder.seed_robot_types(manufacturer_id)
            print("🤖 Robot database initialized with Unitree robots")
        else:
            print(f"🤖 Robot database already has {count} robot types")
            
        seeder.close()
        
    except Exception as e:
        print(f"⚠️ Error initializing robot database: {e}")
