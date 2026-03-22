"""
Multi-Environment Client Setup

Supports any environment type with appropriate knowledge bases,
procedures, and configurations.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from uuid import uuid4

from .multi_tenant_rag import MultiTenantRAG, ClientContext
from .knowledge_base import KnowledgeBaseManager


class EnvironmentType:
    """Supported environment types with their characteristics."""
    
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    HEALTHCARE = "healthcare"
    EDUCATIONAL = "educational"
    RETAIL = "retail"
    LOGISTICS = "logistics"
    HOSPITALITY = "hospitality"
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        return [
            cls.RESIDENTIAL,
            cls.COMMERCIAL,
            cls.INDUSTRIAL,
            cls.HEALTHCARE,
            cls.EDUCATIONAL,
            cls.RETAIL,
            cls.LOGISTICS,
            cls.HOSPITALITY
        ]
    
    @classmethod
    def get_display_name(cls, env_type: str) -> str:
        display_names = {
            cls.RESIDENTIAL: "Residential (Home/Cottage)",
            cls.COMMERCIAL: "Commercial (Office/Business)",
            cls.INDUSTRIAL: "Industrial (Factory/Warehouse)",
            cls.HEALTHCARE: "Healthcare (Hospital/Clinic)",
            cls.EDUCATIONAL: "Educational (School/University)",
            cls.RETAIL: "Retail (Store/Shop)",
            cls.LOGISTICS: "Logistics (Distribution/Shipping)",
            cls.HOSPITALITY: "Hospitality (Hotel/Restaurant)"
        }
        return display_names.get(env_type, env_type.title())


class EnvironmentKnowledgeBase:
    """Environment-specific knowledge base configurations."""
    
    @staticmethod
    def get_zone_templates(env_type: str) -> List[Dict[str, Any]]:
        """Get zone templates for specific environment type."""
        
        templates = {
            EnvironmentType.RESIDENTIAL: [
                {
                    "name": "kitchen",
                    "type": "food_preparation",
                    "description": "Food preparation and dining area",
                    "common_tasks": ["cooking", "cleaning", "food_storage", "dishwashing"],
                    "landmarks": ["refrigerator", "stove", "sink", "counters", "dining_table"],
                    "constraints": ["food_safety", "cleanliness", "appliance_safety"]
                },
                {
                    "name": "living_room",
                    "type": "social_space",
                    "description": "Main living and entertainment area",
                    "common_tasks": ["tidying", "entertainment_setup", "guest_assistance", "cleaning"],
                    "landmarks": ["sofa", "tv", "coffee_table", "entertainment_center"],
                    "constraints": ["comfort", "safety", "noise_consideration"]
                },
                {
                    "name": "bedroom",
                    "type": "private_space",
                    "description": "Private sleeping and rest area",
                    "common_tasks": ["bed_making", "organization", "cleaning", "laundry_assistance"],
                    "landmarks": ["bed", "wardrobe", "dresser", "nightstand"],
                    "constraints": ["privacy", "quiet_operation", "comfort"]
                },
                {
                    "name": "bathroom",
                    "type": "hygiene",
                    "description": "Personal hygiene and grooming area",
                    "common_tasks": ["cleaning", "supply_restock", "maintenance_check"],
                    "landmarks": ["toilet", "sink", "shower", "medicine_cabinet"],
                    "constraints": ["water_safety", "hygiene", "ventilation"]
                }
            ],
            
            EnvironmentType.COMMERCIAL: [
                {
                    "name": "reception",
                    "type": "entry_point",
                    "description": "Main reception and visitor area",
                    "common_tasks": ["visitor_assistance", "security_monitoring", "information_provision"],
                    "landmarks": ["reception_desk", "waiting_area", "security_desk", "visitor_badge_system"],
                    "constraints": ["security_protocol", "professional_appearance", "access_control"]
                },
                {
                    "name": "conference_room",
                    "type": "meeting_space",
                    "description": "Meeting and presentation area",
                    "common_tasks": ["room_setup", "equipment_preparation", "cleaning", "refreshment_service"],
                    "landmarks": ["conference_table", "presentation_screen", "whiteboard", "video_conference_system"],
                    "constraints": ["meeting_schedule", "equipment_protection", "noise_level"]
                },
                {
                    "name": "office_space",
                    "type": "work_area",
                    "description": "General office workspace",
                    "common_tasks": ["desk_organization", "supply_delivery", "cleaning", "equipment_maintenance"],
                    "landmarks": ["workstations", "printers", "filing_cabinets", "break_area"],
                    "constraints": ["productivity", "noise_minimization", "equipment_safety"]
                },
                {
                    "name": "break_room",
                    "type": "relaxation",
                    "description": "Employee break and kitchen area",
                    "common_tasks": ["cleaning", "supply_restock", "food_preparation", "maintenance"],
                    "landmarks": ["kitchen_area", "seating", "vending_machines", "coffee_station"],
                    "constraints": ["hygiene", "safety", "employee_comfort"]
                }
            ],
            
            EnvironmentType.INDUSTRIAL: [
                {
                    "name": "production_floor",
                    "type": "manufacturing",
                    "description": "Main production and manufacturing area",
                    "common_tasks": ["material_handling", "equipment_monitoring", "safety_patrol", "maintenance_assistance"],
                    "landmarks": ["production_lines", "workstations", "quality_control_stations", "safety_stations"],
                    "constraints": ["safety_protocols", "equipment_protection", "production_schedule"]
                },
                {
                    "name": "warehouse",
                    "type": "storage",
                    "description": "Storage and logistics area",
                    "common_tasks": ["inventory_management", "order_fulfillment", "stock_organization", "shipping_preparation"],
                    "landmarks": ["storage_racks", "loading_docks", "packing_stations", "inventory_systems"],
                    "constraints": ["inventory_accuracy", "safety_clearance", "loading_protocols"]
                },
                {
                    "name": "maintenance_shop",
                    "type": "service",
                    "description": "Equipment maintenance and repair area",
                    "common_tasks": ["equipment_repair", "tool_organization", "safety_inspection", "parts_inventory"],
                    "landmarks": ["workbenches", "tool_storage", "equipment_lifts", "safety_equipment"],
                    "constraints": ["safety_procedures", "tool_organization", "equipment_protection"]
                },
                {
                    "name": "quality_control",
                    "type": "inspection",
                    "description": "Quality inspection and testing area",
                    "common_tasks": ["product_inspection", "testing_procedures", "documentation", "defect_reporting"],
                    "landmarks": ["inspection_stations", "testing_equipment", "documentation_area", "quarantine_area"],
                    "constraints": ["quality_standards", "testing_protocols", "documentation_accuracy"]
                }
            ],
            
            EnvironmentType.HEALTHCARE: [
                {
                    "name": "reception_area",
                    "type": "patient_entry",
                    "description": "Patient registration and waiting area",
                    "common_tasks": ["patient_assistance", "registration_support", "wayfinding", "information_provision"],
                    "landmarks": ["registration_desk", "waiting_area", "information_desk", "triage_station"],
                    "constraints": ["patient_privacy", "hygiene_protocols", "accessibility", "quiet_operation"]
                },
                {
                    "name": "patient_room",
                    "type": "care_area",
                    "description": "Patient treatment and recovery area",
                    "common_tasks": ["room_preparation", "supply_delivery", "cleaning", "equipment_monitoring"],
                    "landmarks": ["patient_bed", "medical_equipment", "supply_cabinet", "monitoring_systems"],
                    "constraints": ["sterility", "patient_safety", "quiet_operation", "emergency_access"]
                },
                {
                    "name": "pharmacy",
                    "type": "medication",
                    "description": "Medication storage and dispensing area",
                    "common_tasks": ["inventory_management", "medication_preparation", "delivery_service", "stock_organization"],
                    "landmarks": ["medication_storage", "preparation_area", "dispensing_counter", "secure_storage"],
                    "constraints": ["security", "accuracy", "sterility", "regulatory_compliance"]
                },
                {
                    "name": "laboratory",
                    "type": "testing",
                    "description": "Medical testing and analysis area",
                    "common_tasks": ["sample_transport", "equipment_assistance", "cleaning", "supply_management"],
                    "landmarks": ["testing_equipment", "sample_storage", "analysis_stations", "sterile_areas"],
                    "constraints": ["sterility", "sample_integrity", "safety_protocols", "accuracy"]
                }
            ],
            
            EnvironmentType.EDUCATIONAL: [
                {
                    "name": "classroom",
                    "type": "learning_space",
                    "description": "Primary teaching and learning area",
                    "common_tasks": ["room_setup", "equipment_preparation", "cleaning", "supply_distribution"],
                    "landmarks": ["teacher_desk", "student_desks", "whiteboard", "audiovisual_equipment"],
                    "constraints": ["learning_environment", "safety", "equipment_protection", "schedule_adherence"]
                },
                {
                    "name": "library",
                    "type": "study_area",
                    "description": "Resource and study area",
                    "common_tasks": ["book_organization", "assistance_services", "quiet_monitoring", "resource_management"],
                    "landmarks": ["bookshelves", "study_carrels", "reference_desk", "computer_stations"],
                    "constraints": ["quiet_environment", "resource_protection", "accessibility", "study_comfort"]
                },
                {
                    "name": "cafeteria",
                    "type": "dining",
                    "description": "Student and staff dining area",
                    "common_tasks": ["cleaning", "table_setup", "supply_restock", "waste_management"],
                    "landmarks": ["serving_area", "dining_tables", "kitchen", "disposal_area"],
                    "constraints": ["food_safety", "cleanliness", "efficiency", "noise_control"]
                },
                {
                    "name": "gymnasium",
                    "type": "athletic",
                    "description": "Physical education and athletic area",
                    "common_tasks": ["equipment_setup", "safety_monitoring", "cleaning", "maintenance_assistance"],
                    "landmarks": ["sports_equipment", "court_areas", "locker_rooms", "safety_equipment"],
                    "constraints": ["safety", "equipment_protection", "supervision", "maintenance_schedules"]
                }
            ],
            
            EnvironmentType.RETAIL: [
                {
                    "name": "sales_floor",
                    "type": "shopping",
                    "description": "Main customer shopping area",
                    "common_tasks": ["customer_assistance", "product_restock", "display_organization", "cleaning"],
                    "landmarks": ["product_displays", "checkout_counters", "customer_service_desk", "promotion_areas"],
                    "constraints": ["customer_safety", "product_protection", "store_appearance", "efficiency"]
                },
                {
                    "name": "stock_room",
                    "type": "inventory",
                    "description": "Product storage and inventory area",
                    "common_tasks": ["inventory_management", "stock_replenishment", "organization", "order_preparation"],
                    "landmarks": ["storage_shelves", "receiving_area", "packing_stations", "inventory_system"],
                    "constraints": ["inventory_accuracy", "product_protection", "efficiency", "safety"]
                },
                {
                    "name": "checkout_area",
                    "type": "transaction",
                    "description": "Customer payment and service area",
                    "common_tasks": ["checkout_assistance", "bagging_service", "customer_support", "area_maintenance"],
                    "landmarks": ["checkout_counters", "bagging_area", "customer_service", "payment_systems"],
                    "constraints": ["transaction_speed", "customer_service", "security", "organization"]
                },
                {
                    "name": "display_windows",
                    "type": "marketing",
                    "description": "Store front and promotional display area",
                    "common_tasks": ["display_maintenance", "promotion_setup", "cleaning", "lighting_adjustment"],
                    "landmarks": ["display_cases", "promotional_materials", "lighting_systems", "entrance_area"],
                    "constraints": ["visual_appeal", "safety", "accessibility", "maintenance_schedules"]
                }
            ],
            
            EnvironmentType.LOGISTICS: [
                {
                    "name": "receiving_dock",
                    "type": "inbound",
                    "description": "Incoming shipments receiving area",
                    "common_tasks": ["unloading", "inspection", "documentation", "sorting"],
                    "landmarks": ["loading_docks", "inspection_stations", "documentation_area", "sorting_conveyors"],
                    "constraints": ["safety_protocols", "inspection_accuracy", "documentation_compliance", "efficiency"]
                },
                {
                    "name": "storage_area",
                    "type": "warehousing",
                    "description": "Main storage and warehousing area",
                    "common_tasks": ["inventory_management", "stock_organization", "order_picking", "space_optimization"],
                    "landmarks": ["storage_racks", "picking_stations", "conveyor_systems", "inventory_systems"],
                    "constraints": ["inventory_accuracy", "space_efficiency", "safety_clearance", "access_optimization"]
                },
                {
                    "name": "shipping_area",
                    "type": "outbound",
                    "description": "Outbound shipment preparation area",
                    "common_tasks": ["order_packing", "shipping_preparation", "documentation", "loading"],
                    "landmarks": ["packing_stations", "shipping_docks", "documentation_area", "quality_control"],
                    "constraints": ["shipping_accuracy", "packaging_quality", "documentation_compliance", "loading_safety"]
                },
                {
                    "name": "cross_dock",
                    "type": "transfer",
                    "description": "Direct transfer and sorting area",
                    "common_tasks": ["sorting", "transfer_coordination", "temporary_storage", "distribution"],
                    "landmarks": ["sorting_conveyors", "transfer_stations", "temporary_storage", "distribution_areas"],
                    "constraints": ["transfer_speed", "sorting_accuracy", "space_utilization", "coordination"]
                }
            ],
            
            EnvironmentType.HOSPITALITY: [
                {
                    "name": "lobby",
                    "type": "guest_entry",
                    "description": "Guest reception and check-in area",
                    "common_tasks": ["guest_assistance", "luggage_handling", "information_provision", "check_in_support"],
                    "landmarks": ["reception_desk", "seating_area", "concierge_desk", "luggage_storage"],
                    "constraints": ["guest_service", "security", "appearance", "efficiency"]
                },
                {
                    "name": "guest_room",
                    "type": "accommodation",
                    "description": "Guest sleeping and accommodation area",
                    "common_tasks": ["room_preparation", "cleaning", "amenity_restock", "maintenance_assistance"],
                    "landmarks": ["bed", "bathroom", "work_area", "amenity_station"],
                    "constraints": ["guest_privacy", "cleanliness_standards", "quiet_operation", "amenity_quality"]
                },
                {
                    "name": "restaurant",
                    "type": "dining",
                    "description": "Guest dining and restaurant area",
                    "common_tasks": ["table_service", "cleaning", "supply_restock", "guest_assistance"],
                    "landmarks": ["dining_tables", "kitchen_area", "bar", "host_stand"],
                    "constraints": ["service_quality", "food_safety", "guest_comfort", "efficiency"]
                },
                {
                    "name": "conference_facility",
                    "type": "events",
                    "description": "Meeting and event hosting area",
                    "common_tasks": ["room_setup", "event_support", "cleaning", "equipment_management"],
                    "landmarks": ["meeting_rooms", "event_spaces", "audiovisual_equipment", "service_areas"],
                    "constraints": ["event_coordination", "equipment_protection", "service_quality", "flexibility"]
                }
            ]
        }
        
        return templates.get(env_type, [])
    
    @staticmethod
    def get_mission_templates(env_type: str) -> List[Dict[str, Any]]:
        """Get mission templates for specific environment type."""
        
        base_templates = [
            {
                "type": "inspection",
                "description": "Systematic inspection of areas and equipment",
                "procedures": ["Define inspection area", "Select appropriate robot", "Execute inspection", "Document findings"],
                "robot_recommendations": {"indoor": "humanoid", "outdoor": "quadruped", "aerial": "drone"}
            },
            {
                "type": "transport",
                "description": "Movement of items between locations",
                "procedures": ["Identify item characteristics", "Plan route", "Execute transport", "Verify delivery"],
                "robot_recommendations": {"light": "humanoid", "medium": "quadruped", "heavy": "cargo"}
            },
            {
                "type": "cleaning",
                "description": "Cleaning and maintenance tasks",
                "procedures": ["Assess cleaning needs", "Select supplies", "Execute cleaning", "Inspect results"],
                "robot_recommendations": {"detailed": "humanoid", "general": "quadruped", "heavy": "cargo"}
            }
        ]
        
        # Add environment-specific missions
        env_specific = {
            EnvironmentType.RESIDENTIAL: [
                {
                    "type": "home_assistance",
                    "description": "General home assistance and support",
                    "procedures": ["Understand needs", "Provide assistance", "Monitor satisfaction", "Document outcomes"],
                    "robot_recommendations": {"personal": "humanoid", "general": "quadruped", "emergency": "cargo"}
                }
            ],
            
            EnvironmentType.COMMERCIAL: [
                {
                    "type": "office_support",
                    "description": "Office environment support and assistance",
                    "procedures": ["Assess office needs", "Provide support services", "Maintain productivity", "Ensure comfort"],
                    "robot_recommendations": {"administrative": "humanoid", "general": "quadruped", "logistics": "cargo"}
                }
            ],
            
            EnvironmentType.INDUSTRIAL: [
                {
                    "type": "production_support",
                    "description": "Production and manufacturing support",
                    "procedures": ["Monitor production", "Assist workflows", "Ensure safety", "Maintain efficiency"],
                    "robot_recommendations": {"precision": "humanoid", "general": "quadruped", "heavy": "cargo"}
                }
            ],
            
            EnvironmentType.HEALTHCARE: [
                {
                    "type": "healthcare_support",
                    "description": "Healthcare environment support and assistance",
                    "procedures": ["Follow protocols", "Assist staff", "Ensure safety", "Maintain sterility"],
                    "robot_recommendations": {"patient": "humanoid", "general": "quadruped", "emergency": "cargo"}
                }
            ],
            
            EnvironmentType.EDUCATIONAL: [
                {
                    "type": "education_support",
                    "description": "Educational environment support and assistance",
                    "procedures": ["Support learning", "Maintain environment", "Assist staff", "Ensure safety"],
                    "robot_recommendations": ["humanoid", "quadruped"]
                }
            ],
            
            EnvironmentType.RETAIL: [
                {
                    "type": "retail_support",
                    "description": "Retail environment support and customer service",
                    "procedures": ["Assist customers", "Maintain displays", "Manage inventory", "Ensure safety"],
                    "robot_recommendations": {"customer": "humanoid", "general": "quadruped", "inventory": "cargo"}
                }
            ],
            
            EnvironmentType.LOGISTICS: [
                {
                    "type": "logistics_support",
                    "description": "Logistics and supply chain support",
                    "procedures": ["Manage inventory", "Coordinate shipments", "Optimize workflows", "Ensure accuracy"],
                    "robot_recommendations": {"precision": "humanoid", "general": "quadruped", "heavy": "cargo"}
                }
            ],
            
            EnvironmentType.HOSPITALITY: [
                {
                    "type": "hospitality_support",
                    "description": "Hospitality and guest service support",
                    "procedures": ["Assist guests", "Maintain facilities", "Provide services", "Ensure comfort"],
                    "robot_recommendations": {"guest": "humanoid", "general": "quadruped", "service": "cargo"}
                }
            ]
        }
        
        return base_templates + env_specific.get(env_type, [])
    
    @staticmethod
    def get_safety_procedures(env_type: str) -> List[Dict[str, Any]]:
        """Get safety procedures for specific environment type."""
        
        base_safety = [
            {
                "category": "emergency",
                "title": "Emergency Response Protocol",
                "description": "Procedures for handling emergency situations",
                "steps": ["Stop operations", "Assess hazards", "Contact emergency services", "Evacuate if needed", "Document incident"]
            }
        ]
        
        env_specific = {
            EnvironmentType.HEALTHCARE: [
                {
                    "category": "medical",
                    "title": "Medical Emergency Protocol",
                    "description": "Healthcare-specific emergency procedures",
                    "steps": ["Activate medical emergency response", "Protect patients", "Assist medical staff", "Maintain sterility", "Document events"]
                },
                {
                    "category": "infection_control",
                    "title": "Infection Control Protocol",
                    "description": "Infection prevention and control procedures",
                    "steps": ["Follow PPE protocols", "Maintain sterility", "Implement isolation procedures", "Document exposures", "Follow decontamination"]
                }
            ],
            
            EnvironmentType.INDUSTRIAL: [
                {
                    "category": "industrial_safety",
                    "title": "Industrial Safety Protocol",
                    "description": "Industrial environment safety procedures",
                    "steps": ["Lockout/tagout equipment", "Clear work areas", "Use PPE", "Follow safety procedures", "Report hazards"]
                },
                {
                    "category": "hazardous_materials",
                    "title": "Hazardous Materials Protocol",
                    "description": "Handling hazardous materials safely",
                    "steps": ["Identify materials", "Use proper PPE", "Follow handling procedures", "Implement containment", "Report incidents"]
                }
            ],
            
            EnvironmentType.RETAIL: [
                {
                    "category": "customer_safety",
                    "title": "Customer Safety Protocol",
                    "description": "Customer and public safety procedures",
                    "steps": ["Ensure customer safety", "Clear hazards", "Provide assistance", "Maintain order", "Document incidents"]
                }
            ]
        }
        
        return base_safety + env_specific.get(env_type, [])


class MultiEnvironmentSetup:
    """Setup system for multiple environment types."""
    
    def __init__(self):
        self.base_path = Path("data/rag")
        self.setup_complete = False
    
    async def initialize_environment(self, env_config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a new environment client."""
        env_type = env_config.get("type", EnvironmentType.RESIDENTIAL)
        
        if env_type not in EnvironmentType.get_all_types():
            return {
                "success": False,
                "error": f"Unsupported environment type: {env_type}",
                "supported_types": EnvironmentType.get_all_types()
            }
        
        print(f"🌍 Initializing {EnvironmentType.get_display_name(env_type)}...")
        
        try:
            # 1. Create directory structure
            await self._create_directory_structure()
            
            # 2. Initialize RAG system
            rag_system = await self._initialize_rag_system()
            
            # 3. Register environment client
            client_id = await self._register_environment_client(rag_system, env_config)
            
            # 4. Populate environment knowledge
            await self._populate_environment_knowledge(rag_system, client_id, env_type)
            
            # 5. Setup monitoring
            await self._setup_monitoring(rag_system, client_id, env_type)
            
            self.setup_complete = True
            
            return {
                "success": True,
                "client_id": client_id,
                "environment_type": env_type,
                "display_name": EnvironmentType.get_display_name(env_type),
                "rag_system": "initialized",
                "knowledge_base": "populated",
                "monitoring": "active",
                "setup_time": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "environment_type": env_type
            }
    
    async def _create_directory_structure(self) -> None:
        """Create RAG directory structure."""
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
    
    async def _initialize_rag_system(self) -> MultiTenantRAG:
        """Initialize the multi-tenant RAG system."""
        rag_system = MultiTenantRAG(
            base_db_path="data/rag/shared_knowledge.db",
            client_storage_path="data/rag/clients"
        )
        
        await rag_system.initialize()
        return rag_system
    
    async def _register_environment_client(self, rag_system: MultiTenantRAG, env_config: Dict[str, Any]) -> str:
        """Register environment client with appropriate configuration."""
        env_type = env_config.get("type", EnvironmentType.RESIDENTIAL)
        
        # Environment-specific configuration
        env_configs = {
            EnvironmentType.RESIDENTIAL: {
                "storage_quota": {"documents": 5000, "embeddings": 25000, "memory_mb": 500},
                "features": {"voice_commands": True, "personal_assistance": True, "privacy_protection": True},
                "privacy_settings": {"data_sharing": "anonymized_only", "retention_days": 365}
            },
            EnvironmentType.COMMERCIAL: {
                "storage_quota": {"documents": 10000, "embeddings": 50000, "memory_mb": 1000},
                "features": {"office_support": True, "meeting_assistance": True, "security_monitoring": True},
                "privacy_settings": {"data_sharing": "corporate_policy", "retention_days": 730}
            },
            EnvironmentType.INDUSTRIAL: {
                "storage_quota": {"documents": 15000, "embeddings": 75000, "memory_mb": 2000},
                "features": {"production_support": True, "safety_monitoring": True, "heavy_duty": True},
                "privacy_settings": {"data_sharing": "compliance_required", "retention_days": 1825}
            },
            EnvironmentType.HEALTHCARE: {
                "storage_quota": {"documents": 12000, "embeddings": 60000, "memory_mb": 1500},
                "features": {"patient_support": True, "sterility_monitoring": True, "emergency_response": True},
                "privacy_settings": {"data_sharing": "hipaa_compliant", "retention_days": 2555}
            },
            EnvironmentType.EDUCATIONAL: {
                "storage_quota": {"documents": 8000, "embeddings": 40000, "memory_mb": 800},
                "features": {"education_support": True, "safety_monitoring": True, "accessibility": True},
                "privacy_settings": {"data_sharing": "ferpa_compliant", "retention_days": 1095}
            },
            EnvironmentType.RETAIL: {
                "storage_quota": {"documents": 10000, "embeddings": 50000, "memory_mb": 1000},
                "features": {"customer_service": True, "inventory_management": True, "security_monitoring": True},
                "privacy_settings": {"data_sharing": "corporate_policy", "retention_days": 730}
            },
            EnvironmentType.LOGISTICS: {
                "storage_quota": {"documents": 15000, "embeddings": 75000, "memory_mb": 2000},
                "features": {"logistics_support": True, "inventory_management": True, "coordination": True},
                "privacy_settings": {"data_sharing": "supply_chain_partners", "retention_days": 1095}
            },
            EnvironmentType.HOSPITALITY: {
                "storage_quota": {"documents": 8000, "embeddings": 40000, "memory_mb": 800},
                "features": {"guest_services": True, "facility_management": True, "event_support": True},
                "privacy_settings": {"data_sharing": "guest_privacy", "retention_days": 365}
            }
        }
        
        # Merge base config with environment-specific config
        base_config = {
            "name": env_config.get("name", f"{env_type.title()} Instance"),
            "type": env_type,
            "description": env_config.get("description", f"{EnvironmentType.get_display_name(env_type)} with automation capabilities"),
            "location": env_config.get("location", "unspecified"),
            "knowledge_base": "hybrid"
        }
        
        env_specific_config = env_configs.get(env_type, env_configs[EnvironmentType.RESIDENTIAL])
        base_config.update(env_specific_config)
        
        client_id = await rag_system.register_client(base_config)
        return client_id
    
    async def _populate_environment_knowledge(self, rag_system: MultiTenantRAG, client_id: str, env_type: str) -> None:
        """Populate environment-specific knowledge base."""
        knowledge_manager = EnvironmentKnowledgeManager(rag_system)
        
        # Add shared knowledge
        await knowledge_manager.add_shared_knowledge()
        
        # Add environment-specific knowledge
        await knowledge_manager.add_environment_knowledge(client_id, env_type)
        
        # Add robot capabilities (adapted for environment)
        await knowledge_manager.add_adapted_robot_knowledge(client_id, env_type)
    
    async def _setup_monitoring(self, rag_system: MultiTenantRAG, client_id: str, env_type: str) -> None:
        """Setup environment-specific monitoring."""
        monitoring_config = {
            "client_id": client_id,
            "environment_type": env_type,
            "metrics_collection": {
                "query_performance": True,
                "knowledge_usage": True,
                "error_tracking": True,
                "resource_utilization": True
            },
            "alerts": {
                "slow_queries": {"threshold_ms": 2000, "enabled": True},
                "low_accuracy": {"threshold": 0.8, "enabled": True},
                "storage_quota": {"threshold_percent": 90, "enabled": True}
            },
            "maintenance": {
                "auto_cleanup": {"enabled": True, "frequency": "daily"},
                "backup_schedule": {"enabled": True, "frequency": "weekly"},
                "index_rebuild": {"enabled": True, "frequency": "monthly"}
            }
        }
        
        await rag_system.setup_monitoring(client_id, monitoring_config)


class EnvironmentKnowledgeManager:
    """Manages environment-specific knowledge population."""
    
    def __init__(self, rag_system: MultiTenantRAG):
        self.rag_system = rag_system
    
    async def add_shared_knowledge(self) -> None:
        """Add shared knowledge available to all environments."""
        # Add robot capabilities
        await self._add_robot_capabilities()
        
        # Add base mission templates
        await self._add_base_mission_templates()
        
        # Add base safety procedures
        await self._add_base_safety_procedures()
    
    async def add_environment_knowledge(self, client_id: str, env_type: str) -> None:
        """Add environment-specific knowledge."""
        # Add zone templates
        await self._add_zone_templates(client_id, env_type)
        
        # Add mission templates
        await self._add_mission_templates(client_id, env_type)
        
        # Add safety procedures
        await self._add_safety_procedures(client_id, env_type)
    
    async def add_adapted_robot_knowledge(self, client_id: str, env_type: str) -> None:
        """Add robot capabilities adapted for specific environment."""
        # Get base robot knowledge
        robots = [
            {
                "type": "quadruped",
                "description": "Four-legged robot with outdoor navigation capabilities",
                "capabilities": ["outdoor_navigation", "rough_terrain_handling", "payload_transport"],
                "limitations": ["fine_manipulation", "indoor_narrow_spaces"],
                "preferred_tasks": self._get_preferred_tasks_for_env("quadruped", env_type)
            },
            {
                "type": "humanoid",
                "description": "Two-legged robot with fine manipulation capabilities",
                "capabilities": ["fine_manipulation", "indoor_navigation", "human_interaction"],
                "limitations": ["payload_capacity", "outdoor_rough_terrain"],
                "preferred_tasks": self._get_preferred_tasks_for_env("humanoid", env_type)
            },
            {
                "type": "cargo",
                "description": "Heavy-duty robot for large payload transport",
                "capabilities": ["heavy_payload_transport", "large_cargo_space", "stability"],
                "limitations": ["fine_manipulation", "indoor_narrow_spaces"],
                "preferred_tasks": self._get_preferred_tasks_for_env("cargo", env_type)
            },
            {
                "type": "drone",
                "description": "Aerial robot for surveillance and inspection",
                "capabilities": ["aerial_surveillance", "quick_inspection", "area_mapping"],
                "limitations": ["payload_weight", "indoor_operation", "battery_life"],
                "preferred_tasks": self._get_preferred_tasks_for_env("drone", env_type)
            }
        ]
        
        for robot in robots:
            await self.rag_system.add_document(
                client_id=client_id,
                document={
                    "id": f"robot_{robot['type']}_adapted",
                    "content": json.dumps(robot, indent=2),
                    "metadata": {
                        "type": "robot",
                        "category": "capabilities",
                        "robot_type": robot["type"],
                        "environment": env_type,
                        "scope": "client_specific"
                    }
                }
            )
    
    def _get_preferred_tasks_for_env(self, robot_type: str, env_type: str) -> List[str]:
        """Get preferred tasks adapted for environment."""
        
        base_tasks = {
            "quadruped": ["outdoor_navigation", "patrol", "transport"],
            "humanoid": ["assistance", "manipulation", "interaction"],
            "cargo": ["heavy_transport", "logistics", "storage"],
            "drone": ["surveillance", "inspection", "quick_delivery"]
        }
        
        env_adaptations = {
            EnvironmentType.RESIDENTIAL: {
                "quadruped": ["yard_maintenance", "outdoor_security", "package_transport"],
                "humanoid": ["home_assistance", "cleaning", "organization"],
                "cargo": ["furniture_moving", "bulk_storage", "seasonal_items"],
                "drone": ["property_survey", "security_patrol", "quick_inspection"]
            },
            EnvironmentType.COMMERCIAL: {
                "quadruped": ["facility_patrol", "document_transport", "security"],
                "humanoid": ["office_assistance", "meeting_support", "reception"],
                "cargo": ["equipment_moving", "supply_delivery", "maintenance"],
                "drone": ["facility_inspection", "security_monitoring", "delivery"]
            },
            EnvironmentType.INDUSTRIAL: {
                "quadruped": ["facility_inspection", "material_transport", "safety_patrol"],
                "humanoid": ["precision_tasks", "equipment_operation", "quality_control"],
                "cargo": ["heavy_material_handling", "logistics", "production_support"],
                "drone": ["aerial_inspection", "site_survey", "emergency_monitoring"]
            },
            EnvironmentType.HEALTHCARE: {
                "quadruped": ["facility_patrol", "supply_transport", "emergency_response"],
                "humanoid": ["patient_assistance", "sterile_tasks", "equipment_operation"],
                "cargo": ["medical_supply_transport", "waste_management", "equipment_moving"],
                "drone": ["emergency_response", "facility_monitoring", "quick_delivery"]
            }
        }
        
        return env_adaptations.get(env_type, {}).get(robot_type, base_tasks.get(robot_type, []))
    
    async def _add_zone_templates(self, client_id: str, env_type: str) -> None:
        """Add zone templates for environment."""
        zones = EnvironmentKnowledgeBase.get_zone_templates(env_type)
        
        for zone in zones:
            await self.rag_system.add_document(
                client_id=client_id,
                document={
                    "id": f"zone_{zone['name']}",
                    "content": json.dumps(zone, indent=2),
                    "metadata": {
                        "type": "zone",
                        "category": "environment_layout",
                        "zone_name": zone["name"],
                        "zone_type": zone["type"],
                        "environment": env_type,
                        "scope": "client_specific"
                    }
                }
            )
    
    async def _add_mission_templates(self, client_id: str, env_type: str) -> None:
        """Add mission templates for environment."""
        missions = EnvironmentKnowledgeBase.get_mission_templates(env_type)
        
        for mission in missions:
            await self.rag_system.add_document(
                client_id=client_id,
                document={
                    "id": f"mission_{mission['type']}",
                    "content": json.dumps(mission, indent=2),
                    "metadata": {
                        "type": "mission",
                        "category": "templates",
                        "mission_type": mission["type"],
                        "environment": env_type,
                        "scope": "client_specific"
                    }
                }
            )
    
    async def _add_safety_procedures(self, client_id: str, env_type: str) -> None:
        """Add safety procedures for environment."""
        procedures = EnvironmentKnowledgeBase.get_safety_procedures(env_type)
        
        for procedure in procedures:
            await self.rag_system.add_document(
                client_id=client_id,
                document={
                    "id": f"safety_{procedure['category']}",
                    "content": json.dumps(procedure, indent=2),
                    "metadata": {
                        "type": "safety",
                        "category": procedure["category"],
                        "environment": env_type,
                        "scope": "client_specific"
                    }
                }
            )
    
    async def _add_robot_capabilities(self) -> None:
        """Add shared robot capabilities."""
        # This would be implemented similar to the original KnowledgeBaseManager
        pass
    
    async def _add_base_mission_templates(self) -> None:
        """Add base mission templates."""
        # This would be implemented similar to the original KnowledgeBaseManager
        pass
    
    async def _add_base_safety_procedures(self) -> None:
        """Add base safety procedures."""
        # This would be implemented similar to the original KnowledgeBaseManager
        pass


# Setup execution functions
async def setup_cottage_first():
    """Setup cottage as first instance (backward compatibility)."""
    setup = MultiEnvironmentSetup()
    
    cottage_config = {
        "name": "Cottage",
        "type": EnvironmentType.RESIDENTIAL,
        "description": "Primary cottage residence with full automation capabilities",
        "location": "primary_residence"
    }
    
    return await setup.initialize_environment(cottage_config)


async def setup_environment(env_config: Dict[str, Any]):
    """Setup any environment type."""
    setup = MultiEnvironmentSetup()
    return await setup.initialize_environment(env_config)


if __name__ == "__main__":
    async def demo_multi_environment():
        """Demonstrate multi-environment setup."""
        print("🌍 Multi-Environment RAG Setup Demo")
        print("=" * 50)
        
        setup = MultiEnvironmentSetup()
        
        # Setup different environment types
        environments = [
            {
                "name": "Cottage",
                "type": EnvironmentType.RESIDENTIAL,
                "description": "Primary residence",
                "location": "countryside"
            },
            {
                "name": "Office Building",
                "type": EnvironmentType.COMMERCIAL,
                "description": "Corporate office building",
                "location": "downtown"
            },
            {
                "name": "Factory",
                "type": EnvironmentType.INDUSTRIAL,
                "description": "Manufacturing facility",
                "location": "industrial_park"
            },
            {
                "name": "Hospital",
                "type": EnvironmentType.HEALTHCARE,
                "description": "Medical facility",
                "location": "medical_center"
            }
        ]
        
        for env_config in environments:
            print(f"\n🏢 Setting up {env_config['name']}...")
            result = await setup.initialize_environment(env_config)
            
            if result["success"]:
                print(f"✅ {env_config['name']} setup complete!")
                print(f"   Client ID: {result['client_id']}")
                print(f"   Environment: {result['display_name']}")
            else:
                print(f"❌ {env_config['name']} setup failed!")
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 50)
        print("🎯 Multi-Environment Setup Demo Complete!")
    
    asyncio.run(demo_multi_environment())
