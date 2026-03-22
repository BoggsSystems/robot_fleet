#!/usr/bin/env python3
"""
Unitree Robots Database Seeding Script
Populates the database with Unitree robot models and specifications
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any

# Unitree robot specifications
UNITREE_ROBOTS = [
    {
        "manufacturer": "Unitree",
        "model": "A1",
        "robot_type": "delivery",
        "capabilities": ["package_delivery", "navigation", "obstacle_avoidance", "climbing", "dynamic_balance"],
        "specifications": {
            "weight_capacity": 5.0,  # kg
            "battery_life_hours": 2.0,
            "max_speed_kmh": 6.0,
            "navigation_system": "LiDAR + Visual SLAM",
            "sensor_suite": ["LiDAR", "Depth Camera", "IMU", "Force Sensors"],
            "dimensions": {"length": 0.5, "width": 0.3, "height": 0.4},  # meters
            "weight_kg": 12.0,
            "operating_temperature_range": "-10°C to 40°C",
            "ip_rating": "IP54",
            "connectivity_options": ["WiFi", "4G", "Bluetooth"],
            "payload_types": ["small_packages", "documents", "medical_supplies"],
            "climbing_ability": "stairs and obstacles up to 20cm"
        },
        "price_currency": "USD",
        "price_amount": 16000.0,
        "availability_status": "available",
        "support_level": "premium",
        "documentation_url": "https://www.unitree.com/a1/docs",
        "image_url": "https://www.unitree.com/a1/image.jpg",
        "data_sheet_url": "https://www.unitree.com/a1/datasheet.pdf"
    },
    {
        "manufacturer": "Unitree",
        "model": "Go1",
        "robot_type": "security",
        "capabilities": ["surveillance", "patrol", "alert_system", "human_detection", "night_vision"],
        "specifications": {
            "weight_capacity": 3.0,
            "battery_life_hours": 2.5,
            "max_speed_kmh": 4.5,
            "navigation_system": "Visual SLAM + GPS",
            "sensor_suite": ["RGB Camera", "Thermal Camera", "IMU", "Microphone Array"],
            "dimensions": {"length": 0.6, "width": 0.35, "height": 0.5},
            "weight_kg": 15.0,
            "operating_temperature_range": "-20°C to 45°C",
            "ip_rating": "IP65",
            "connectivity_options": ["WiFi", "4G", "LoRa"],
            "patrol_duration_hours": 8.0,
            "detection_range_meters": 50.0,
            "night_vision_range_meters": 30.0
        },
        "price_currency": "USD",
        "price_amount": 18000.0,
        "availability_status": "available",
        "support_level": "premium",
        "documentation_url": "https://www.unitree.com/go1/docs",
        "image_url": "https://www.unitree.com/go1/image.jpg",
        "data_sheet_url": "https://www.unitree.com/go1/datasheet.pdf"
    },
    {
        "manufacturer": "Unitree",
        "model": "Aliengo",
        "robot_type": "inspection",
        "capabilities": ["visual_inspection", "sensor_monitoring", "reporting", "thermal_imaging", "gas_detection"],
        "specifications": {
            "weight_capacity": 2.0,
            "battery_life_hours": 3.0,
            "max_speed_kmh": 3.5,
            "navigation_system": "LiDAR + RTK GPS",
            "sensor_suite": ["High-Res Camera", "Thermal Camera", "Gas Sensors", "LIDAR"],
            "dimensions": {"length": 0.7, "width": 0.4, "height": 0.6},
            "weight_kg": 18.0,
            "operating_temperature_range": "-20°C to 50°C",
            "ip_rating": "IP67",
            "connectivity_options": ["WiFi", "4G", "Ethernet"],
            "inspection_accuracy_mm": 0.1,
            "thermal_resolution": "640x480",
            "gas_sensors": ["CO2", "Methane", "Hydrogen"]
        },
        "price_currency": "USD",
        "price_amount": 25000.0,
        "availability_status": "available",
        "support_level": "enterprise",
        "documentation_url": "https://www.unitree.com/aliengo/docs",
        "image_url": "https://www.unitree.com/aliengo/image.jpg",
        "data_sheet_url": "https://www.unitree.com/aliengo/datasheet.pdf"
    },
    {
        "manufacturer": "Unitree",
        "model": "Z1",
        "robot_type": "maintenance",
        "capabilities": ["diagnostics", "repair_assistance", "preventive_maintenance", "tool_carrying", "remote_operation"],
        "specifications": {
            "weight_capacity": 10.0,
            "battery_life_hours": 4.0,
            "max_speed_kmh": 2.0,
            "navigation_system": "LiDAR + Visual SLAM",
            "sensor_suite": ["3D Camera", "Force Sensors", "Vibration Sensors", "IMU"],
            "dimensions": {"length": 0.8, "width": 0.5, "height": 0.7},
            "weight_kg": 25.0,
            "operating_temperature_range": "-10°C to 40°C",
            "ip_rating": "IP54",
            "connectivity_options": ["WiFi", "4G", "Ethernet"],
            "tool_mount_points": 4,
            "max_tool_weight_kg": 5.0,
            "precision_mm": 1.0
        },
        "price_currency": "USD",
        "price_amount": 35000.0,
        "availability_status": "available",
        "support_level": "enterprise",
        "documentation_url": "https://www.unitree.com/z1/docs",
        "image_url": "https://www.unitree.com/z1/image.jpg",
        "data_sheet_url": "https://www.unitree.com/z1/datasheet.pdf"
    }
]

class RobotDatabaseSeeder:
    def __init__(self, db_path: str = "data/robot_fleet.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def create_tables(self):
        """Create necessary tables"""
        cursor = self.conn.cursor()
        
        # Robot manufacturers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS robot_manufacturers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                website TEXT,
                support_email TEXT,
                support_phone TEXT,
                warranty_period_months INTEGER,
                certification_standards TEXT,  -- JSON array
                headquarters_location TEXT,
                year_founded INTEGER,
                company_description TEXT,
                logo_url TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Robot types table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS robot_types (
                id TEXT PRIMARY KEY,
                manufacturer_id TEXT,
                manufacturer TEXT NOT NULL,
                model TEXT NOT NULL,
                robot_type TEXT NOT NULL,
                capabilities TEXT,  -- JSON array
                specifications TEXT,  -- JSON object
                weight_capacity REAL,
                battery_life_hours REAL,
                max_speed_kmh REAL,
                navigation_system TEXT,
                sensor_suite TEXT,  -- JSON array
                dimensions TEXT,  -- JSON object
                weight_kg REAL,
                operating_temperature_range TEXT,
                ip_rating TEXT,
                connectivity_options TEXT,  -- JSON array
                price_currency TEXT,
                price_amount REAL,
                availability_status TEXT,
                support_level TEXT,
                documentation_url TEXT,
                image_url TEXT,
                data_sheet_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (manufacturer_id) REFERENCES robot_manufacturers(id)
            )
        """)
        
        # Robot compatibility matrix
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS robot_compatibility (
                id TEXT PRIMARY KEY,
                robot_type_id TEXT,
                environment_type TEXT,
                terrain_types TEXT,  -- JSON array
                weather_conditions TEXT,  -- JSON array
                space_requirements TEXT,  -- JSON object
                power_requirements TEXT,  -- JSON object
                network_requirements TEXT,  -- JSON object
                safety_features TEXT,  -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (robot_type_id) REFERENCES robot_types(id)
            )
        """)
        
        self.conn.commit()
        
    def seed_manufacturers(self):
        """Seed robot manufacturers"""
        cursor = self.conn.cursor()
        
        # Unitree manufacturer
        unitree_data = {
            "id": "unitree_001",
            "name": "Unitree Robotics",
            "website": "https://www.unitree.com",
            "support_email": "support@unitree.com",
            "support_phone": "+86-571-8777-2222",
            "warranty_period_months": 12,
            "certification_standards": ["CE", "FCC", "RoHS"],
            "headquarters_location": "Hangzhou, China",
            "year_founded": 2016,
            "company_description": "Leading quadruped robot manufacturer specializing in advanced robotics and AI",
            "logo_url": "https://www.unitree.com/logo.png"
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO robot_manufacturers 
            (id, name, website, support_email, support_phone, warranty_period_months,
             certification_standards, headquarters_location, year_founded, 
             company_description, logo_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            unitree_data["id"],
            unitree_data["name"],
            unitree_data["website"],
            unitree_data["support_email"],
            unitree_data["support_phone"],
            unitree_data["warranty_period_months"],
            json.dumps(unitree_data["certification_standards"]),
            unitree_data["headquarters_location"],
            unitree_data["year_founded"],
            unitree_data["company_description"],
            unitree_data["logo_url"]
        ))
        
        self.conn.commit()
        return unitree_data["id"]
        
    def seed_robot_types(self, manufacturer_id: str):
        """Seed robot types"""
        cursor = self.conn.cursor()
        
        for robot in UNITREE_ROBOTS:
            robot_id = f"{robot['manufacturer'].lower()}_{robot['model'].lower()}_001"
            
            cursor.execute("""
                INSERT OR REPLACE INTO robot_types 
                (id, manufacturer_id, manufacturer, model, robot_type, capabilities,
                 specifications, weight_capacity, battery_life_hours, max_speed_kmh,
                 navigation_system, sensor_suite, dimensions, weight_kg, 
                 operating_temperature_range, ip_rating, connectivity_options,
                 price_currency, price_amount, availability_status, support_level,
                 documentation_url, image_url, data_sheet_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                robot_id,
                manufacturer_id,
                robot["manufacturer"],
                robot["model"],
                robot["robot_type"],
                json.dumps(robot["capabilities"]),
                json.dumps(robot["specifications"]),
                robot["specifications"]["weight_capacity"],
                robot["specifications"]["battery_life_hours"],
                robot["specifications"]["max_speed_kmh"],
                robot["specifications"]["navigation_system"],
                json.dumps(robot["specifications"]["sensor_suite"]),
                json.dumps(robot["specifications"]["dimensions"]),
                robot["specifications"]["weight_kg"],
                robot["specifications"]["operating_temperature_range"],
                robot["specifications"]["ip_rating"],
                json.dumps(robot["specifications"]["connectivity_options"]),
                robot["price_currency"],
                robot["price_amount"],
                robot["availability_status"],
                robot["support_level"],
                robot["documentation_url"],
                robot["image_url"],
                robot["data_sheet_url"]
            ))
            
            # Seed compatibility data
            self._seed_compatibility_data(robot_id, robot)
            
        self.conn.commit()
        
    def _seed_compatibility_data(self, robot_id: str, robot: Dict[str, Any]):
        """Seed robot compatibility data"""
        cursor = self.conn.cursor()
        
        # Determine compatibility based on robot type and specifications
        compatibility_data = self._get_compatibility_for_robot(robot)
        
        cursor.execute("""
            INSERT OR REPLACE INTO robot_compatibility 
            (id, robot_type_id, environment_type, terrain_types, weather_conditions,
             space_requirements, power_requirements, network_requirements, safety_features)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"compat_{robot_id}",
            robot_id,
            compatibility_data["environment_type"],
            json.dumps(compatibility_data["terrain_types"]),
            json.dumps(compatibility_data["weather_conditions"]),
            json.dumps(compatibility_data["space_requirements"]),
            json.dumps(compatibility_data["power_requirements"]),
            json.dumps(compatibility_data["network_requirements"]),
            json.dumps(compatibility_data["safety_features"])
        ))
        
    def _get_compatibility_for_robot(self, robot: Dict[str, Any]) -> Dict[str, Any]:
        """Get compatibility data for a robot based on its type and specs"""
        base_compatibility = {
            "terrain_types": ["flat", "carpet", "tile", "concrete"],
            "weather_conditions": ["dry", "indoor"],
            "space_requirements": {
                "min_corridor_width_m": 1.0,
                "min_door_height_m": 2.0,
                "min_elevator_size_m2": 2.0
            },
            "power_requirements": {
                "voltage": "220V",
                "amperage": 10,
                "charging_time_hours": 2.0
            },
            "network_requirements": {
                "min_bandwidth_mbps": 10,
                "protocols": ["WiFi", "4G"],
                "latency_ms": 100
            },
            "safety_features": ["emergency_stop", "obstacle_detection", "fall_detection"]
        }
        
        # Customize based on robot type
        if robot["robot_type"] == "delivery":
            base_compatibility.update({
                "environment_type": "mixed",
                "terrain_types": ["flat", "carpet", "tile", "concrete", "stairs"],
                "weather_conditions": ["dry", "light_rain", "indoor"],
                "safety_features": ["emergency_stop", "obstacle_detection", "fall_detection", "payload_monitoring"]
            })
        elif robot["robot_type"] == "security":
            base_compatibility.update({
                "environment_type": "outdoor",
                "terrain_types": ["flat", "grass", "gravel", "concrete"],
                "weather_conditions": ["dry", "light_rain", "night"],
                "safety_features": ["emergency_stop", "obstacle_detection", "human_detection", "alert_system"]
            })
        elif robot["robot_type"] == "inspection":
            base_compatibility.update({
                "environment_type": "mixed",
                "terrain_types": ["flat", "rugged", "industrial_floor"],
                "weather_conditions": ["dry", "wet", "extreme_temperatures"],
                "safety_features": ["emergency_stop", "obstacle_detection", "gas_detection", "thermal_monitoring"]
            })
        elif robot["robot_type"] == "maintenance":
            base_compatibility.update({
                "environment_type": "indoor",
                "terrain_types": ["flat", "workshop_floor", "factory_floor"],
                "weather_conditions": ["indoor"],
                "safety_features": ["emergency_stop", "obstacle_detection", "tool_safety", "precision_control"]
            })
            
        return base_compatibility
        
    def get_robot_types_for_fleet_config(self) -> List[Dict[str, Any]]:
        """Get robot types formatted for fleet configuration UI"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT id, manufacturer, model, robot_type, capabilities, specifications,
                   weight_capacity, battery_life_hours, max_speed_kmh, navigation_system,
                   price_amount, availability_status, image_url
            FROM robot_types 
            WHERE availability_status = 'available'
            ORDER BY manufacturer, model
        """)
        
        robots = []
        for row in cursor.fetchall():
            robot_data = dict(row)
            robot_data["capabilities"] = json.loads(robot_data["capabilities"])
            robot_data["specifications"] = json.loads(robot_data["specifications"])
            robots.append(robot_data)
            
        return robots
        
    def get_robot_by_id(self, robot_id: str) -> Dict[str, Any]:
        """Get detailed robot information by ID"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT rt.*, rm.name as manufacturer_name, rm.website as manufacturer_website
            FROM robot_types rt
            JOIN robot_manufacturers rm ON rt.manufacturer_id = rm.id
            WHERE rt.id = ?
        """, (robot_id,))
        
        row = cursor.fetchone()
        if row:
            robot_data = dict(row)
            robot_data["capabilities"] = json.loads(robot_data["capabilities"])
            robot_data["specifications"] = json.loads(robot_data["specifications"])
            return robot_data
        return None
        
    def search_robots(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search robots based on filters"""
        cursor = self.conn.cursor()
        
        query = """
            SELECT id, manufacturer, model, robot_type, capabilities, specifications,
                   weight_capacity, battery_life_hours, max_speed_kmh, navigation_system,
                   price_amount, availability_status, image_url
            FROM robot_types 
            WHERE availability_status = 'available'
        """
        params = []
        
        if filters.get("robot_type"):
            query += " AND robot_type = ?"
            params.append(filters["robot_type"])
            
        if filters.get("manufacturer"):
            query += " AND manufacturer = ?"
            params.append(filters["manufacturer"])
            
        if filters.get("min_payload"):
            query += " AND weight_capacity >= ?"
            params.append(filters["min_payload"])
            
        if filters.get("max_price"):
            query += " AND price_amount <= ?"
            params.append(filters["max_price"])
            
        query += " ORDER BY manufacturer, model"
        
        cursor.execute(query, params)
        
        robots = []
        for row in cursor.fetchall():
            robot_data = dict(row)
            robot_data["capabilities"] = json.loads(robot_data["capabilities"])
            robot_data["specifications"] = json.loads(robot_data["specifications"])
            robots.append(robot_data)
            
        return robots

def main():
    """Main function to seed the database"""
    seeder = RobotDatabaseSeeder()
    
    try:
        seeder.connect()
        print("📦 Connected to database")
        
        seeder.create_tables()
        print("🏗️  Created tables")
        
        manufacturer_id = seeder.seed_manufacturers()
        print(f"🏭 Seeded manufacturers: {manufacturer_id}")
        
        seeder.seed_robot_types(manufacturer_id)
        print("🤖 Seeded robot types")
        
        # Test the data
        robots = seeder.get_robot_types_for_fleet_config()
        print(f"✅ Found {len(robots)} available robots for fleet configuration")
        
        for robot in robots:
            print(f"  - {robot['manufacturer']} {robot['model']} ({robot['robot_type']})")
            
        print("\n🎉 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
    finally:
        seeder.close()
        print("🔒 Database connection closed")

if __name__ == "__main__":
    main()
