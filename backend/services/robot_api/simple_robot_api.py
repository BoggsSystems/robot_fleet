#!/usr/bin/env python3
"""
Simple Robot API Server
Standalone server for robot fleet configuration API
"""

import sqlite3
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Robot Fleet API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Robot database path
ROBOT_DB_PATH = "/Users/jeffboggs/robot_fleet/fleet_control/brain/data/robot_fleet.db"

def get_robot_db_connection():
    """Get robot database connection"""
    return sqlite3.connect(ROBOT_DB_PATH)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Robot Fleet API is running", "version": "1.0.0"}

@app.get("/api/robots/types")
async def get_robot_types():
    """Get all available robot types for fleet configuration"""
    try:
        conn = get_robot_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, manufacturer, model, robot_type, capabilities, specifications,
                   weight_capacity, battery_life_hours, max_speed_kmh, navigation_system,
                   price_amount, availability_status, image_url, documentation_url, data_sheet_url
            FROM robot_types 
            WHERE availability_status = 'available'
            ORDER BY manufacturer, model
        """)
        
        robots = []
        for row in cursor.fetchall():
            robot_data = {
                "id": row[0],
                "manufacturer": row[1],
                "model": row[2],
                "robot_type": row[3],
                "capabilities": json.loads(row[4]),
                "specifications": json.loads(row[5]),
                "weight_capacity": row[6],
                "battery_life_hours": row[7],
                "max_speed_kmh": row[8],
                "navigation_system": row[9],
                "price_amount": row[10],
                "availability_status": row[11],
                "image_url": row[12],
                "documentation_url": row[13],
                "data_sheet_url": row[14]
            }
            robots.append(robot_data)
            
        conn.close()
        print(f"✅ Returning {len(robots)} robots from database")
        return robots
        
    except Exception as e:
        print(f"❌ Error fetching robot types: {e}")
        return []

@app.get("/api/robots/types/{robot_id}")
async def get_robot_type_by_id(robot_id: str):
    """Get detailed information about a specific robot type"""
    try:
        conn = get_robot_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rt.*, rm.name as manufacturer_name, rm.website as manufacturer_website
            FROM robot_types rt
            JOIN robot_manufacturers rm ON rt.manufacturer_id = rm.id
            WHERE rt.id = ?
        """, (robot_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Robot not found")
            
        robot_data = {
            "id": row[0],
            "manufacturer": row[2],
            "model": row[3],
            "robot_type": row[4],
            "capabilities": json.loads(row[5]),
            "specifications": json.loads(row[6]),
            "weight_capacity": row[7],
            "battery_life_hours": row[8],
            "max_speed_kmh": row[9],
            "navigation_system": row[10],
            "price_amount": row[11],
            "availability_status": row[12],
            "image_url": row[13],
            "documentation_url": row[14],
            "data_sheet_url": row[15]
        }
        
        conn.close()
        return robot_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching robot type: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching robot type: {str(e)}")

@app.get("/api/robots/manufacturers")
async def get_manufacturers():
    """Get all robot manufacturers"""
    try:
        conn = get_robot_db_connection()
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
        print(f"❌ Error fetching manufacturers: {e}")
        return []

@app.get("/api/robots/capabilities")
async def get_capabilities():
    """Get all available robot capabilities"""
    try:
        conn = get_robot_db_connection()
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
        print(f"❌ Error fetching capabilities: {e}")
        return []

if __name__ == "__main__":
    print("🚀 Starting Simple Robot API Server on http://localhost:8002")
    print("📡 Available endpoints:")
    print("   GET /api/robots/types")
    print("   GET /api/robots/types/{robot_id}")
    print("   GET /api/robots/manufacturers")
    print("   GET /api/robots/capabilities")
    uvicorn.run(app, host="0.0.0.0", port=8002)
