"""
Knowledge Base Manager

Manages population and organization of knowledge bases for RAG system.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone

from .multi_tenant_rag import MultiTenantRAG


class KnowledgeBaseManager:
    """Manages knowledge base population and organization."""
    
    def __init__(self, rag_system: MultiTenantRAG):
        self.rag_system = rag_system
        self.knowledge_base_path = Path("data/knowledge_base")
        self.knowledge_base_path.mkdir(parents=True, exist_ok=True)
    
    async def add_shared_knowledge(self) -> None:
        """Add shared knowledge available to all clients."""
        print("📚 Adding shared knowledge...")
        
        # Add robot capabilities
        await self._add_robot_capabilities()
        
        # Add mission templates
        await self._add_mission_templates()
        
        # Add safety procedures
        await self._add_safety_procedures()
        
        # Add maintenance procedures
        await self._add_maintenance_procedures()
        
        print("✅ Shared knowledge added")
    
    async def add_cottage_specific_knowledge(self, client_id: str) -> None:
        """Add cottage-specific knowledge for the first instance."""
        print("🏠 Adding cottage-specific knowledge...")
        
        # Add cottage zones
        await self._add_cottage_zones(client_id)
        
        # Add cottage layouts
        await self._add_cottage_layouts(client_id)
        
        # Add cottage procedures
        await self._add_cottage_procedures(client_id)
        
        # Add cottage items and workflows
        await self._add_cottage_items(client_id)
        
        print("✅ Cottage-specific knowledge added")
    
    async def add_robot_knowledge(self) -> None:
        """Add robot capability knowledge."""
        robots = [
            {
                "type": "quadruped",
                "description": "Four-legged robot with outdoor navigation capabilities",
                "capabilities": [
                    "outdoor_navigation",
                    "rough_terrain_handling", 
                    "payload_transport",
                    "stair_climbing",
                    "weather_resistance",
                    "long_range_operation"
                ],
                "limitations": [
                    "fine_manipulation",
                    "indoor_narrow_spaces",
                    "quiet_operation",
                    "high_precision_tasks"
                ],
                "preferred_tasks": [
                    "outdoor_delivery",
                    "patrol",
                    "heavy_transport",
                    "terrain_inspection",
                    "yard_maintenance"
                ],
                "specifications": {
                    "payload_capacity": "12.5kg",
                    "battery_life": "2-3 hours",
                    "speed": "1.5 m/s",
                    "climbing_angle": "30 degrees",
                    "weather_rating": "IP54"
                }
            },
            {
                "type": "humanoid",
                "description": "Two-legged robot with fine manipulation capabilities",
                "capabilities": [
                    "fine_manipulation",
                    "indoor_navigation",
                    "human_interaction",
                    "tool_use",
                    "object_recognition",
                    "gesture_communication"
                ],
                "limitations": [
                    "payload_capacity",
                    "outdoor_rough_terrain",
                    "battery_life",
                    "stability_on_uneven_surfaces"
                ],
                "preferred_tasks": [
                    "object_manipulation",
                    "indoor_assistance",
                    "tool_operation",
                    "human_interaction",
                    "precision_tasks"
                ],
                "specifications": {
                    "payload_capacity": "5kg",
                    "battery_life": "1.5-2 hours",
                    "speed": "1.0 m/s",
                    "hand_grip_force": "10kg",
                    "height": "1.7m"
                }
            },
            {
                "type": "cargo",
                "description": "Heavy-duty robot for large payload transport",
                "capabilities": [
                    "heavy_payload_transport",
                    "large_cargo_space",
                    "stability",
                    "long_range_operation",
                    "automated_loading",
                    "fleet_coordination"
                ],
                "limitations": [
                    "fine_manipulation",
                    "indoor_narrow_spaces",
                    "stair_navigation",
                    "quick_turning"
                ],
                "preferred_tasks": [
                    "bulk_transport",
                    "supply_delivery",
                    "waste_collection",
                    "equipment_moving",
                    "logistics_coordination"
                ],
                "specifications": {
                    "payload_capacity": "50kg",
                    "battery_life": "4-6 hours",
                    "speed": "0.8 m/s",
                    "cargo_volume": "2 cubic meters",
                    "loading_height": "0.5m"
                }
            },
            {
                "type": "drone",
                "description": "Aerial robot for surveillance and inspection",
                "capabilities": [
                    "aerial_surveillance",
                    "quick_inspection",
                    "area_mapping",
                    "package_delivery",
                    "emergency_response",
                    "weather_monitoring"
                ],
                "limitations": [
                    "payload_weight",
                    "indoor_operation",
                    "battery_life",
                    "weather_sensitivity",
                    "noise_restrictions"
                ],
                "preferred_tasks": [
                    "aerial_inspection",
                    "area_survey",
                    "quick_delivery",
                    "security_patrol",
                    "emergency_assessment"
                ],
                "specifications": {
                    "payload_capacity": "2kg",
                    "battery_life": "25-30 minutes",
                    "speed": "15 m/s",
                    "flight_range": "5km",
                    "operating_altitude": "120m"
                }
            }
        ]
        
        for robot in robots:
            await self.rag_system.add_document(
                client_id="shared",
                document={
                    "id": f"robot_{robot['type']}",
                    "content": json.dumps(robot, indent=2),
                    "metadata": {
                        "type": "robot",
                        "category": "capabilities",
                        "robot_type": robot["type"],
                        "scope": "shared"
                    }
                }
            )
    
    async def add_mission_templates(self) -> None:
        """Add mission template knowledge."""
        missions = [
            {
                "type": "inspection",
                "description": "Systematic inspection of areas and equipment",
                "procedures": [
                    "Define inspection area and objectives",
                    "Select appropriate robot based on terrain",
                    "Configure inspection parameters (scan type, duration)",
                    "Execute inspection with systematic coverage",
                    "Document findings and anomalies",
                    "Generate inspection report"
                ],
                "robot_recommendations": {
                    "indoor": "humanoid",
                    "outdoor": "quadruped", 
                    "aerial": "drone",
                    "large_area": "cargo"
                },
                "common_variations": [
                    "qr_code_scan",
                    "safety_inspection",
                    "inventory_check",
                    "damage_assessment",
                    "maintenance_inspection"
                ],
                "success_criteria": [
                    "Complete area coverage",
                    "All required data collected",
                    "Anomalies identified and documented",
                    "Report generated and delivered"
                ]
            },
            {
                "type": "transport",
                "description": "Movement of items between locations",
                "procedures": [
                    "Identify item characteristics (weight, size, fragility)",
                    "Determine optimal robot for transport",
                    "Plan route considering obstacles and constraints",
                    "Prepare item for transport (packaging, securing)",
                    "Execute transport with monitoring",
                    "Verify delivery completion and condition"
                ],
                "robot_recommendations": {
                    "light_items": "humanoid",
                    "medium_items": "quadruped",
                    "heavy_items": "cargo",
                    "urgent_delivery": "drone"
                },
                "common_variations": [
                    "package_delivery",
                    "grocery_transport",
                    "equipment_moving",
                    "waste_collection",
                    "supply_restocking"
                ],
                "success_criteria": [
                    "Item delivered to correct location",
                    "Item remains undamaged",
                    "Delivery within time constraints",
                    "Proper documentation completed"
                ]
            },
            {
                "type": "cleaning",
                "description": "Cleaning and maintenance tasks",
                "procedures": [
                    "Assess cleaning area and requirements",
                    "Select appropriate cleaning supplies and equipment",
                    "Choose robot based on cleaning type and location",
                    "Execute cleaning with systematic approach",
                    "Inspect results and address missed areas",
                    "Restock supplies and maintain equipment"
                ],
                "robot_recommendations": {
                    "surface_cleaning": "humanoid",
                    "floor_cleaning": "quadruped",
                    "outdoor_cleaning": "cargo",
                    "high_reach_cleaning": "drone"
                },
                "common_variations": [
                    "surface_wiping",
                    "vacuum_cleaning",
                    "window_cleaning",
                    "outdoor_maintenance",
                    "deep_cleaning"
                ],
                "success_criteria": [
                    "Area meets cleanliness standards",
                    "No damage to surfaces or items",
                    "Supplies properly restocked",
                    "Time efficiency targets met"
                ]
            },
            {
                "type": "assistance",
                "description": "General assistance and support tasks",
                "procedures": [
                    "Understand user needs and preferences",
                    "Select appropriate assistance approach",
                    "Choose robot based on task requirements",
                    "Execute assistance with attention to user comfort",
                    "Monitor user satisfaction and adjust approach",
                    "Document assistance outcomes and improvements"
                ],
                "robot_recommendations": {
                    "personal_assistance": "humanoid",
                    "mobility_assistance": "quadruped",
                    "emergency_response": "cargo",
                    "quick_tasks": "drone"
                },
                "common_variations": [
                    "human_interaction",
                    "object_retrieval",
                    "emergency_response",
                    "personal_assistance",
                    "guest_support"
                ],
                "success_criteria": [
                    "User needs adequately addressed",
                    "Positive user experience maintained",
                    "Task completed efficiently",
                    "User privacy and comfort respected"
                ]
            }
        ]
        
        for mission in missions:
            await self.rag_system.add_document(
                client_id="shared",
                document={
                    "id": f"mission_{mission['type']}",
                    "content": json.dumps(mission, indent=2),
                    "metadata": {
                        "type": "mission",
                        "category": "templates",
                        "mission_type": mission["type"],
                        "scope": "shared"
                    }
                }
            )
    
    async def add_safety_procedures(self) -> None:
        """Add safety procedure knowledge."""
        safety_procedures = [
            {
                "category": "emergency",
                "title": "Emergency Response Protocol",
                "description": "Procedures for handling emergency situations",
                "steps": [
                    "Immediately stop all robot operations",
                    "Assess situation and identify hazards",
                    "Contact emergency services if required",
                    "Evacuate area if necessary",
                    "Document incident and response actions",
                    "Review and update procedures based on incident"
                ],
                "robot_specific": {
                    "quadruped": "Secure outdoor areas, prevent access to hazards",
                    "humanoid": "Assist with evacuation if safe to do so",
                    "cargo": "Clear evacuation paths, move obstacles",
                    "drone": "Provide aerial overview for emergency responders"
                }
            },
            {
                "category": "maintenance",
                "title": "Robot Maintenance Safety",
                "description": "Safety procedures for robot maintenance",
                "steps": [
                    "Power down robot completely before maintenance",
                    "Use proper tools and follow manufacturer guidelines",
                    "Wear appropriate personal protective equipment",
                    "Test robot operation after maintenance in safe area",
                    "Document maintenance performed and issues found",
                    "Update maintenance schedule based on findings"
                ],
                "requirements": {
                    "tools": ["manufacturer_toolkit", "safety_gloves", "safety_glasses"],
                    "environment": "well_lit_area", "adequate_space", "clean_workspace",
                    "training": "manufacturer_certification", "safety_training"
                }
            },
            {
                "category": "operation",
                "title": "Safe Operation Guidelines",
                "description": "General safety guidelines for robot operation",
                "guidelines": [
                    "Always supervise robot operation in occupied areas",
                    "Maintain safe distance from moving robots",
                    "Ensure robots have adequate battery for planned tasks",
                    "Check area for hazards before robot operation",
                    "Use appropriate robot for environmental conditions",
                    "Follow manufacturer weight and capacity limits"
                ],
                "environmental_considerations": {
                    "weather": "Avoid outdoor operation in severe weather",
                    "lighting": "Ensure adequate lighting for navigation",
                    "obstacles": "Clear area of potential hazards",
                    "people": "Maintain safe distance from humans and pets"
                }
            }
        ]
        
        for procedure in safety_procedures:
            await self.rag_system.add_document(
                client_id="shared",
                document={
                    "id": f"safety_{procedure['category']}",
                    "content": json.dumps(procedure, indent=2),
                    "metadata": {
                        "type": "safety",
                        "category": procedure["category"],
                        "title": procedure["title"],
                        "scope": "shared"
                    }
                }
            )
    
    async def add_maintenance_procedures(self) -> None:
        """Add maintenance procedure knowledge."""
        maintenance = [
            {
                "robot_type": "quadruped",
                "schedule": {
                    "daily": ["visual_inspection", "battery_check", "sensor_cleaning"],
                    "weekly": ["joint_lubrication", "software_update_check", "performance_test"],
                    "monthly": ["deep_cleaning", "calibration_check", "wear_inspection"],
                    "quarterly": ["major_service", "firmware_update", "component_replacement"]
                },
                "procedures": {
                    "battery_check": "Inspect battery level, connections, and charging system",
                    "visual_inspection": "Check for damage, loose parts, or wear indicators",
                    "joint_lubrication": "Apply manufacturer-recommended lubricant to moving joints",
                    "performance_test": "Run standard movement and capability tests"
                },
                "troubleshooting": {
                    "unresponsive": "Check battery, connections, and restart system",
                    "movement_issues": "Check for obstacles, sensor calibration, and joint function",
                    "battery_drain": "Check for software issues, battery health, and charging efficiency"
                }
            },
            {
                "robot_type": "humanoid",
                "schedule": {
                    "daily": ["hand_mechanism_check", "battery_check", "sensor_calibration"],
                    "weekly": ["arm_lubrication", "grip_test", "balance_check"],
                    "monthly": ["deep_cleaning", "software_update", "wear_inspection"],
                    "quarterly": ["major_service", "firmware_update", "component_replacement"]
                },
                "procedures": {
                    "hand_mechanism_check": "Test grip strength, finger movement, and tactile sensors",
                    "sensor_calibration": "Calibrate vision, proximity, and balance sensors",
                    "arm_lubrication": "Lubricate shoulder, elbow, and wrist joints"
                },
                "troubleshooting": {
                    "grip_issues": "Check hand sensors, lubrication, and calibration",
                    "balance_problems": "Check gyro sensors, foot sensors, and weight distribution",
                    "communication_errors": "Check network connections and software status"
                }
            },
            {
                "robot_type": "cargo",
                "schedule": {
                    "daily": ["cargo_system_check", "battery_inspection", "safety_systems_test"],
                    "weekly": ["loading_mechanism_test", "tire_pressure_check", "brake_system_test"],
                    "monthly": ["deep_cleaning", "software_update", "structural_inspection"],
                    "quarterly": ["major_service", "firmware_update", "wear_part_replacement"]
                },
                "procedures": {
                    "cargo_system_check": "Test loading mechanisms, securing systems, and weight sensors",
                    "safety_systems_test": "Test emergency stops, collision avoidance, and warning systems"
                },
                "troubleshooting": {
                    "loading_issues": "Check hydraulic systems, sensors, and alignment",
                    "mobility_problems": "Check tires, motors, and navigation systems",
                    "power_issues": "Check battery systems, charging, and power distribution"
                }
            },
            {
                "robot_type": "drone",
                "schedule": {
                    "daily": ["propeller_check", "battery_inspection", "gps_signal_test"],
                    "weekly": ["flight_test", "camera_calibration", "firmware_check"],
                    "monthly": ["deep_cleaning", "sensor_calibration", "structural_inspection"],
                    "quarterly": ["major_service", "firmware_update", "component_replacement"]
                },
                "procedures": {
                    "propeller_check": "Inspect for damage, balance, and secure attachment",
                    "flight_test": "Perform basic flight maneuvers and stability checks"
                },
                "troubleshooting": {
                    "flight_instability": "Check propellers, calibration, and environmental conditions",
                    "gps_issues": "Check antenna, signal strength, and location accuracy",
                    "battery_problems": "Check charging, health, and temperature management"
                }
            }
        ]
        
        for robot_maintenance in maintenance:
            await self.rag_system.add_document(
                client_id="shared",
                document={
                    "id": f"maintenance_{robot_maintenance['robot_type']}",
                    "content": json.dumps(robot_maintenance, indent=2),
                    "metadata": {
                        "type": "maintenance",
                        "category": "procedures",
                        "robot_type": robot_maintenance["robot_type"],
                        "scope": "shared"
                    }
                }
            )
    
    async def _add_cottage_zones(self, client_id: str) -> None:
        """Add cottage zone knowledge."""
        from .cottage_first_setup import CottageKnowledgePopulator
        populator = CottageKnowledgePopulator(self.rag_system)
        await populator.add_cottage_zones(client_id)
    
    async def _add_cottage_layouts(self, client_id: str) -> None:
        """Add cottage layout knowledge."""
        from .cottage_first_setup import CottageKnowledgePopulator
        populator = CottageKnowledgePopulator(self.rag_system)
        await populator.add_cottage_layouts(client_id)
    
    async def _add_cottage_procedures(self, client_id: str) -> None:
        """Add cottage-specific procedures."""
        procedures = [
            {
                "name": "daily_closing_procedure",
                "description": "End-of-day security and preparation procedures",
                "steps": [
                    "Check all doors and windows are secured",
                    "Verify alarm system is activated",
                    "Ensure all robots are docked and charging",
                    "Check outdoor area for security concerns",
                    "Review security camera footage",
                    "Set overnight monitoring protocols"
                ],
                "robot_involvement": {
                    "quadruped": "Perform outdoor perimeter check",
                    "humanoid": "Assist with indoor security verification",
                    "drone": "Conduct aerial security survey"
                }
            },
            {
                "name": "morning_preparation_procedure",
                "description": "Morning routine preparation procedures",
                "steps": [
                    "Check overnight security status",
                    "Prepare coffee and breakfast areas",
                    "Review daily schedule and priorities",
                    "Check weather and outdoor conditions",
                    "Prepare robots for daily tasks",
                    "Review any overnight alerts or issues"
                ],
                "robot_involvement": {
                    "humanoid": "Prepare kitchen area and breakfast setup",
                    "quadruped": "Check outdoor conditions and weather station",
                    "drone": "Quick aerial survey of property"
                }
            },
            {
                "name": "guest_preparation_procedure",
                "description": "Procedures for preparing for guests",
                "steps": [
                    "Clean and organize common areas",
                    "Prepare guest room with fresh linens",
                    "Check bathroom supplies and cleanliness",
                    "Prepare welcome amenities",
                    "Review guest preferences and requirements",
                    "Adjust robot behaviors for guest comfort"
                ],
                "robot_involvement": {
                    "humanoid": "Room preparation and amenity setup",
                    "quadruped": "Outdoor area cleaning and preparation",
                    "cargo": "Transport supplies and equipment"
                }
            }
        ]
        
        for procedure in procedures:
            await self.rag_system.add_document(
                client_id=client_id,
                document={
                    "id": f"procedure_{procedure['name']}",
                    "content": json.dumps(procedure, indent=2),
                    "metadata": {
                        "type": "procedure",
                        "category": "cottage_specific",
                        "procedure_name": procedure["name"],
                        "scope": "client_specific"
                    }
                }
            )
    
    async def _add_cottage_items(self, client_id: str) -> None:
        """Add cottage items and workflows knowledge."""
        items = [
            {
                "name": "groceries",
                "description": "Food and household supplies management",
                "typical_locations": ["kitchen_refrigerator", "kitchen_pantry", "kitchen_counters"],
                "handling_requirements": ["temperature_control", "careful_handling", "separation_by_type"],
                "common_destinations": ["kitchen", "refrigerator", "pantry", "counters"],
                "workflow": {
                    "arrival": "Inspect for damage, sort by type, check expiration dates",
                    "storage": "Refrigerate perishables, organize pantry, stock counters",
                    "inventory": "Update inventory list, note low items, plan restocking",
                    "usage": "Monitor consumption, plan meals, minimize waste"
                },
                "robot_recommendations": {
                    "transport": "quadruped for dock to kitchen transport",
                    "organization": "humanoid for detailed sorting and placement",
                    "inventory": "humanoid for detailed inspection and recording"
                }
            },
            {
                "name": "packages",
                "description": "Package and delivery management",
                "typical_locations": ["dock", "front_door", "garage", "porch"],
                "handling_requirements": ["careful_handling", "recipient_verification", "damage_inspection"],
                "common_destinations": ["living_room", "bedroom", "office", "kitchen"],
                "workflow": {
                    "receiving": "Verify recipient, inspect for damage, document condition",
                    "sorting": "Organize by recipient, urgency, and storage requirements",
                    "delivery": "Deliver to appropriate location, notify recipient",
                    "follow_up": "Confirm receipt satisfaction, document delivery"
                },
                "robot_recommendations": {
                    "transport": "quadruped for most deliveries",
                    "verification": "humanoid for detailed inspection and verification",
                    "urgent": "drone for time-critical small packages"
                }
            },
            {
                "name": "cleaning_supplies",
                "description": "Cleaning and maintenance supplies management",
                "typical_locations": ["bathroom_cabinet", "cleaning_closet", "kitchen_under_sink", "garage"],
                "handling_requirements": ["segregated_storage", "accessibility", "safety_considerations"],
                "common_destinations": ["cleaning_areas", "storage_locations", "usage_points"],
                "workflow": {
                    "inventory": "Check supply levels, note low items, plan restocking",
                    "organization": "Group by type and usage area, ensure accessibility",
                    "usage": "Select appropriate supplies for task, use safely",
                    "restocking": "Purchase replacements, organize new supplies"
                },
                "robot_recommendations": {
                    "organization": "humanoid for detailed organization and inventory",
                    "transport": "quadruped for moving supplies between areas",
                    "application": "humanoid for detailed cleaning tasks"
                }
            }
        ]
        
        for item in items:
            await self.rag_system.add_document(
                client_id=client_id,
                document={
                    "id": f"item_{item['name']}",
                    "content": json.dumps(item, indent=2),
                    "metadata": {
                        "type": "item",
                        "category": "cottage_items",
                        "item_name": item["name"],
                        "scope": "client_specific"
                    }
                }
            )


if __name__ == "__main__":
    # Test knowledge base manager
    import asyncio
    from .multi_tenant_rag import MultiTenantRAG
    
    async def test_knowledge_base():
        rag = MultiTenantRAG("data/test_rag.db", "data/test_clients")
        await rag.initialize()
        
        client_id = await rag.register_client({
            "type": "cottage",
            "description": "Test cottage instance"
        })
        
        manager = KnowledgeBaseManager(rag)
        await manager.add_shared_knowledge()
        await manager.add_cottage_specific_knowledge(client_id)
        
        # Test search
        results = await rag.search(client_id, "kitchen cleaning")
        print(f"Search results: {len(results)} documents found")
        
        for result in results:
            print(f"- {result['id']}: {result['similarity_score']:.3f}")
    
    asyncio.run(test_knowledge_base())
