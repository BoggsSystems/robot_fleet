"""
Multi-Client RAG System Setup

Initializes the first cottage instance with complete knowledge base,
client management, and scalable RAG architecture.
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import uuid4

from .multi_tenant_rag import MultiTenantRAG, ClientRegistry, ClientContext
from .knowledge_base import KnowledgeBaseManager


class CottageInstanceSetup:
    """Setup and manage the first cottage instance."""
    
    def __init__(self):
        self.base_path = Path("data/rag")
        self.setup_complete = False
        
    async def initialize_first_instance(self) -> Dict[str, Any]:
        """Initialize the cottage as the first RAG instance."""
        print("🏠 Initializing Cottage as First RAG Instance...")
        
        try:
            # 1. Create directory structure
            await self._create_directory_structure()
            
            # 2. Initialize multi-tenant RAG system
            rag_system = await self._initialize_rag_system()
            
            # 3. Register cottage as first client
            client_id = await self._register_cottage_client(rag_system)
            
            # 4. Populate cottage knowledge base
            await self._populate_cottage_knowledge(rag_system, client_id)
            
            # 5. Setup monitoring and maintenance
            await self._setup_monitoring(rag_system, client_id)
            
            self.setup_complete = True
            
            return {
                "success": True,
                "client_id": client_id,
                "rag_system": "initialized",
                "knowledge_base": "populated",
                "monitoring": "active",
                "instance_type": "cottage_first",
                "setup_time": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stage": self._get_error_stage(e)
            }
    
    async def _create_directory_structure(self) -> None:
        """Create the RAG directory structure."""
        print("📁 Creating directory structure...")
        
        directories = [
            "data/rag",
            "data/rag/shared",
            "data/rag/shared/knowledge",
            "data/rag/shared/robots", 
            "data/rag/shared/missions",
            "data/rag/shared/procedures",
            "data/rag/clients",
            "data/rag/indexes",
            "data/rag/cache",
            "data/rag/logs",
            "data/rag/backups"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        print("✅ Directory structure created")
    
    async def _initialize_rag_system(self) -> MultiTenantRAG:
        """Initialize the multi-tenant RAG system."""
        print("🧠 Initializing RAG system...")
        
        rag_system = MultiTenantRAG(
            base_db_path="data/rag/shared_knowledge.db",
            client_storage_path="data/rag/clients"
        )
        
        await rag_system.initialize()
        
        print("✅ RAG system initialized")
        return rag_system
    
    async def _register_cottage_client(self, rag_system: MultiTenantRAG) -> str:
        """Register the cottage as the first client."""
        print("🏠 Registering cottage as first client...")
        
        client_config = {
            "name": "Cottage",
            "type": "cottage",
            "description": "Primary cottage residence with full automation capabilities",
            "location": "primary_residence",
            "knowledge_base": "hybrid",  # shared + personal
            "storage_quota": {
                "documents": 10000,      # 10k documents
                "embeddings": 50000,      # 50k embeddings  
                "memory_mb": 1000,        # 1GB memory
                "cache_mb": 500           # 500MB cache
            },
            "features": {
                "voice_commands": True,
                "visual_recognition": True,
                "predictive_assistance": True,
                "multi_robot_coordination": True,
                "emergency_response": True
            },
            "privacy_settings": {
                "data_sharing": "anonymized_only",
                "retention_days": 365,
                "analytics_opt_in": True
            }
        }
        
        client_id = await rag_system.register_client(client_config)
        
        print(f"✅ Cottage registered with client_id: {client_id}")
        return client_id
    
    async def _populate_cottage_knowledge(self, rag_system: MultiTenantRAG, client_id: str) -> None:
        """Populate the cottage knowledge base with initial content."""
        print("📚 Populating cottage knowledge base...")
        
        knowledge_manager = KnowledgeBaseManager(rag_system)
        
        # 1. Add shared cottage knowledge
        await knowledge_manager.add_shared_knowledge()
        
        # 2. Add cottage-specific knowledge
        await knowledge_manager.add_cottage_specific_knowledge(client_id)
        
        # 3. Add robot capability knowledge
        await knowledge_manager.add_robot_knowledge()
        
        # 4. Add mission templates
        await knowledge_manager.add_mission_templates()
        
        # 5. Add procedural knowledge
        await knowledge_manager.add_procedural_knowledge()
        
        print("✅ Cottage knowledge base populated")
    
    async def _setup_monitoring(self, rag_system: MultiTenantRAG, client_id: str) -> None:
        """Setup monitoring and maintenance systems."""
        print("📊 Setting up monitoring...")
        
        # Create monitoring configuration
        monitoring_config = {
            "client_id": client_id,
            "metrics_collection": {
                "query_performance": True,
                "knowledge_usage": True,
                "error_tracking": True,
                "resource_utilization": True
            },
            "alerts": {
                "slow_queries": {"threshold_ms": 2000, "enabled": True},
                "low_accuracy": {"threshold": 0.8, "enabled": True},
                "storage_quota": {"threshold_percent": 90, "enabled": True},
                "system_errors": {"enabled": True}
            },
            "maintenance": {
                "auto_cleanup": {"enabled": True, "frequency": "daily"},
                "backup_schedule": {"enabled": True, "frequency": "weekly"},
                "index_rebuild": {"enabled": True, "frequency": "monthly"}
            }
        }
        
        await rag_system.setup_monitoring(client_id, monitoring_config)
        
        print("✅ Monitoring setup complete")
    
    def _get_error_stage(self, error: Exception) -> str:
        """Determine which setup stage failed."""
        error_str = str(error).lower()
        
        if "directory" in error_str or "permission" in error_str:
            return "directory_creation"
        elif "rag" in error_str or "database" in error_str:
            return "rag_initialization"
        elif "client" in error_str or "register" in error_str:
            return "client_registration"
        elif "knowledge" in error_str or "populate" in error_str:
            return "knowledge_population"
        elif "monitoring" in error_str:
            return "monitoring_setup"
        else:
            return "unknown"
    
    async def get_instance_status(self) -> Dict[str, Any]:
        """Get current instance status."""
        if not self.setup_complete:
            return {"status": "not_initialized", "stage": "setup_required"}
        
        return {
            "status": "active",
            "instance_type": "cottage_first",
            "setup_time": self._get_setup_time(),
            "client_count": 1,
            "knowledge_base_status": "populated",
            "rag_system_status": "active",
            "monitoring_status": "active"
        }
    
    def _get_setup_time(self) -> Optional[str]:
        """Get the setup time from metadata."""
        try:
            with open("data/rag/setup_metadata.json", "r") as f:
                metadata = json.load(f)
                return metadata.get("setup_time")
        except (FileNotFoundError, json.JSONDecodeError):
            return None


# Cottage-specific knowledge population
class CottageKnowledgePopulator:
    """Populate cottage-specific knowledge for the first instance."""
    
    def __init__(self, rag_system: MultiTenantRAG):
        self.rag_system = rag_system
    
    async def add_cottage_zones(self, client_id: str) -> None:
        """Add detailed cottage zone knowledge."""
        zones = [
            {
                "name": "kitchen",
                "type": "indoor",
                "description": "Main kitchen area with cooking, food storage, and dining spaces",
                "landmarks": ["refrigerator", "stove", "sink", "dishwasher", "microwave", "coffee_maker", "dining_table"],
                "common_tasks": ["food_preparation", "cooking", "cleaning", "dishwashing", "inventory_check", "food_organization"],
                "constraints": ["no_liquid_spills_near_electronics", "keep_appliances_clear", "temperature_control_for_perishables"],
                "connectivity": ["living_room", "dining_area", "pantry"],
                "typical_items": ["groceries", "cookware", "dishes", "small_appliances", "cleaning_supplies"]
            },
            {
                "name": "living_room",
                "type": "indoor",
                "description": "Primary living and entertainment space",
                "landmarks": ["sofa", "tv_stand", "coffee_table", "bookshelf", "fireplace", "entertainment_center", "side_tables"],
                "common_tasks": ["tidying", "dusting", "vacuuming", "item_retrieval", "guest_assistance", "entertainment_setup"],
                "constraints": ["keep_walkways_clear", "quiet_operation_during_movies", "protect_electronics"],
                "connectivity": ["kitchen", "bedroom", "entrance", "hallway"],
                "typical_items": ["remote_controls", "magazines", "blankets", "decorative_items", "electronics"]
            },
            {
                "name": "bedroom",
                "type": "indoor",
                "description": "Private sleeping and personal space",
                "landmarks": ["bed", "wardrobe", "dresser", "nightstand", "desk", "mirror", "closet"],
                "common_tasks": ["bed_making", "clothing_organization", "cleaning", "laundry_assistance", "item_delivery"],
                "constraints": ["maintain_privacy", "quiet_operation", "respect_personal_space"],
                "connectivity": ["bathroom", "living_room", "closet"],
                "typical_items": ["clothing", "bedding", "personal_items", "books", "electronics"]
            },
            {
                "name": "bathroom",
                "type": "indoor",
                "description": "Personal hygiene and grooming space",
                "landmarks": ["toilet", "sink", "shower", "bathtub", "medicine_cabinet", "mirror", "towel_rack"],
                "common_tasks": ["cleaning", "supply_replacement", "spill_cleanup", "maintenance_check", "inventory_check"],
                "constraints": ["water_safety", "slip_prevention", "ventilation", "chemical_safety"],
                "connectivity": ["bedroom", "hallway"],
                "typical_items": ["toiletries", "towels", "cleaning_supplies", "medications", "first_aid"]
            },
            {
                "name": "dock",
                "type": "outdoor",
                "description": "Loading, unloading, and outdoor storage area",
                "landmarks": ["loading_bay", "storage_shed", "outdoor_faucet", "security_camera", "motion_lights", "package_drop_off"],
                "common_tasks": ["package_handling", "outdoor_cleaning", "yard_maintenance", "security_patrol", "equipment_storage"],
                "constraints": ["weather_considerations", "security_awareness", "proper_weight_distribution"],
                "connectivity": ["garage", "garden", "entrance"],
                "typical_items": ["packages", "outdoor_equipment", "tools", "garden_supplies", "seasonal_items"]
            },
            {
                "name": "garage",
                "type": "mixed",
                "description": "Vehicle storage and workshop area",
                "landmarks": ["workbench", "tool_chest", "vehicle_space", "storage_racks", "charging_station", "overhead_door"],
                "common_tasks": ["vehicle_assistance", "tool_organization", "maintenance", "storage_management", "charging_management"],
                "constraints": ["vehicle_safety", "tool_organization", "adequate_lighting", "fire_safety"],
                "connectivity": ["house", "dock", "yard"],
                "typical_items": ["vehicles", "tools", "equipment", "supplies", "maintenance_items"]
            },
            {
                "name": "garden",
                "type": "outdoor",
                "description": "Outdoor plant and landscape area",
                "landmarks": ["garden_beds", "watering_system", "tool_shed", "compost_bin", "greenhouse", "pathways"],
                "common_tasks": ["plant_care", "watering", "weeding", "harvesting", "lawn_maintenance", "seasonal_planting"],
                "constraints": ["plant_safety", "water_conservation", "weather_monitoring", "pest_control"],
                "connectivity": ["house", "garage", "dock"],
                "typical_items": ["plants", "tools", "seeds", "fertilizer", "garden_equipment", "harvest_baskets"]
            }
        ]
        
        for zone in zones:
            await self.rag_system.add_document(
                client_id=client_id,
                document={
                    "id": f"zone_{zone['name']}",
                    "content": json.dumps(zone, indent=2),
                    "metadata": {
                        "type": "zone",
                        "category": "cottage_layout",
                        "zone_name": zone["name"],
                        "zone_type": zone["type"],
                        "scope": "shared"
                    }
                }
            )
    
    async def add_cottage_layouts(self, client_id: str) -> None:
        """Add cottage layout and navigation knowledge."""
        layouts = [
            {
                "name": "floor_plan",
                "description": "Complete cottage floor plan with room dimensions and connections",
                "content": """
                    The cottage follows a traditional layout with central hallway connecting all main rooms.
                    
                    Room Dimensions:
                    - Kitchen: 15' x 12' with island and dining area
                    - Living Room: 18' x 14' with open concept to dining
                    - Bedroom: 14' x 12' with walk-in closet
                    - Bathroom: 8' x 6' with shower/tub combination
                    - Garage: 20' x 12' with workshop area
                    - Dock: 12' x 8' covered loading area
                    
                    Navigation:
                    - Central hallway provides access to all rooms
                    - Kitchen connects to living room through open archway
                    - Master bedroom has private bathroom access
                    - Garage connects to house through mudroom
                    - Dock has separate exterior access
                    
                    Special Considerations:
                    - All doorways are 36" wide for wheelchair access
                    - Kitchen has multiple work zones for parallel tasks
                    - Living room has high ceiling for fan circulation
                    - Garage has reinforced floor for heavy equipment
                """,
                "metadata": {
                    "type": "layout",
                    "category": "navigation",
                    "scope": "shared"
                }
            },
            {
                "name": "electrical_system",
                "description": "Electrical layout and outlet locations",
                "content": """
                    Electrical System Overview:
                    
                    Power Distribution:
                    - 200A main service panel
                    - Separate circuits for kitchen appliances
                    - GFCI outlets in bathroom and outdoor areas
                    - USB charging outlets in living room and bedroom
                    
                    Outlet Locations:
                    Kitchen: 12 outlets (4 GFCI), 1 dedicated refrigerator circuit
                    Living Room: 8 outlets (2 with USB), 1 ceiling fan circuit
                    Bedroom: 6 outlets (2 with USB), 1 closet light circuit
                    Bathroom: 4 GFCI outlets, 1 exhaust fan circuit
                    Garage: 6 outlets (2 GFCI), 1 workshop circuit
                    Dock: 2 weatherproof outlets, 1 motion light circuit
                    
                    Charging Stations:
                    - Kitchen island: 2 USB-C outlets for devices
                    - Living room: 4-port USB charging station
                    - Bedroom: 2 USB outlets near nightstands
                    - Garage: 1 EV charging station (240V)
                    
                    Safety Features:
                    - Arc fault breakers on all circuits
                    - Surge protection on electronics
                    - Emergency lighting with battery backup
                    - Outdoor lighting on motion sensors
                """,
                "metadata": {
                    "type": "infrastructure",
                    "category": "electrical",
                    "scope": "shared"
                }
            }
        ]
        
        for layout in layouts:
            await self.rag_system.add_document(
                client_id=client_id,
                document={
                    "id": f"layout_{layout['name']}",
                    "content": layout["content"],
                    "metadata": {
                        "type": "layout",
                        "category": layout["category"],
                        "scope": "shared"
                    }
                }
            )


# Setup execution
async def setup_cottage_first_instance():
    """Main setup function for cottage first instance."""
    setup = CottageInstanceSetup()
    
    print("🚀 Starting Cottage First Instance Setup")
    print("=" * 50)
    
    result = await setup.initialize_first_instance()
    
    print("=" * 50)
    
    if result["success"]:
        print("✅ Cottage First Instance Setup Complete!")
        print(f"🏠 Client ID: {result['client_id']}")
        print(f"🧠 RAG System: {result['rag_system']}")
        print(f"📚 Knowledge Base: {result['knowledge_base']}")
        print(f"📊 Monitoring: {result['monitoring']}")
        print(f"⏰ Setup Time: {result['setup_time']}")
        
        print("\n🎯 Next Steps:")
        print("1. Test RAG queries with cottage-specific questions")
        print("2. Add personal preferences and customizations")
        print("3. Integrate with mission planning system")
        print("4. Enable multi-client capabilities")
        
    else:
        print("❌ Setup Failed!")
        print(f"🚨 Error: {result.get('error', 'Unknown error')}")
        print(f"📍 Failed Stage: {result.get('stage', 'unknown')}")
        
        print("\n🔧 Troubleshooting:")
        print("1. Check file permissions for data/rag directory")
        print("2. Verify database dependencies are installed")
        print("3. Ensure sufficient disk space available")
        print("4. Check network connectivity for external APIs")
    
    return result


if __name__ == "__main__":
    asyncio.run(setup_cottage_first_instance())
