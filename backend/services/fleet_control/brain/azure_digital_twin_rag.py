"""
Azure Digital Twins integration with RAG system for enhanced contextual understanding.
"""

from __future__ import annotations

import json
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    from azure.digitaltwins.core import DigitalTwinsClient
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from .multi_tenant_rag import MultiTenantRAG
from .contextual_intent import ContextualIntentService


class AzureDigitalTwinRAGIntegration:
    """Integrate Azure Digital Twin data with RAG system"""
    
    def __init__(self, rag_system: MultiTenantRAG, adt_endpoint: Optional[str] = None):
        self.rag_system = rag_system
        self.adt_endpoint = adt_endpoint
        self.adt_client = None
        self.twin_cache = {}
        self.relationship_cache = {}
        
        if AZURE_AVAILABLE and adt_endpoint:
            self._initialize_azure_client()
    
    def _initialize_azure_client(self):
        """Initialize Azure Digital Twins client"""
        try:
            credential = DefaultAzureCredential()
            self.adt_client = DigitalTwinsClient(
                endpoint=self.adt_endpoint,
                credential=credential
            )
            print("✅ Azure Digital Twins client initialized")
        except Exception as e:
            print(f"⚠️  Failed to initialize Azure Digital Twins client: {e}")
            self.adt_client = None
    
    async def sync_digital_twin_to_rag(self, client_id: str, twin_id: str) -> None:
        """Sync Digital Twin data into RAG knowledge base"""
        if not self.adt_client:
            print("⚠️  Azure Digital Twins client not available")
            return
        
        try:
            # 1. Get Digital Twin data
            twin_data = await self._get_digital_twin(twin_id)
            
            # 2. Extract relevant information
            twin_knowledge = self._extract_twin_knowledge(twin_data)
            
            # 3. Create RAG documents
            for knowledge_item in twin_knowledge:
                await self.rag_system.add_document(
                    client_id=client_id,
                    document={
                        "id": f"digital_twin_{knowledge_item['id']}",
                        "content": json.dumps(knowledge_item['content']),
                        "metadata": {
                            "type": "digital_twin",
                            "category": knowledge_item['category'],
                            "twin_id": twin_id,
                            "twin_type": knowledge_item['twin_type'],
                            "last_sync": datetime.now(timezone.utc).isoformat(),
                            "scope": "client_specific"
                        }
                    }
                )
            
            print(f"✅ Synced Digital Twin {twin_id} to RAG for client {client_id}")
            
        except Exception as e:
            print(f"❌ Failed to sync Digital Twin {twin_id}: {e}")
    
    async def _get_digital_twin(self, twin_id: str) -> Dict[str, Any]:
        """Get Digital Twin data"""
        loop = asyncio.get_event_loop()
        twin_data = await loop.run_in_executor(
            None, 
            self.adt_client.get_digital_twin, 
            twin_id
        )
        return twin_data
    
    def _extract_twin_knowledge(self, twin_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract relevant knowledge from Digital Twin data"""
        knowledge_items = []
        
        twin_id = twin_data["$dtId"]
        twin_type = twin_data.get("$metadata", {}).get("$model", "")
        
        # Extract based on twin type
        if "Zone" in twin_type:
            knowledge_items.append({
                "id": f"zone_{twin_id}",
                "content": self._extract_zone_knowledge(twin_data),
                "category": "zone",
                "twin_type": twin_type
            })
        elif "Robot" in twin_type:
            knowledge_items.append({
                "id": f"robot_{twin_id}",
                "content": self._extract_robot_knowledge(twin_data),
                "category": "robot",
                "twin_type": twin_type
            })
        elif "Cottage" in twin_type:
            knowledge_items.append({
                "id": f"cottage_{twin_id}",
                "content": self._extract_cottage_knowledge(twin_data),
                "category": "cottage",
                "twin_type": twin_type
            })
        else:
            # Generic twin knowledge
            knowledge_items.append({
                "id": f"generic_{twin_id}",
                "content": self._extract_generic_knowledge(twin_data),
                "category": "generic",
                "twin_type": twin_type
            })
        
        return knowledge_items
    
    def _extract_zone_knowledge(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract zone-specific knowledge"""
        return {
            "name": twin_data.get("name", twin_data["$dtId"]),
            "type": twin_data.get("type", "unknown"),
            "description": twin_data.get("description", ""),
            "current_conditions": {
                "temperature": twin_data.get("temperature", 20.0),
                "humidity": twin_data.get("humidity", 50.0),
                "occupancy": twin_data.get("occupancy", 0),
                "lighting_level": twin_data.get("lighting_level", 500),
                "noise_level": twin_data.get("noise_level", 40)
            },
            "landmarks": twin_data.get("landmarks", []),
            "common_tasks": twin_data.get("common_tasks", []),
            "constraints": twin_data.get("constraints", []),
            "connectivity": twin_data.get("connectivity", []),
            "typical_items": twin_data.get("typical_items", []),
            "real_time_constraints": self._generate_constraints_from_conditions(twin_data),
            "optimal_tasks": self._determine_optimal_tasks(twin_data),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    def _extract_robot_knowledge(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract robot-specific knowledge"""
        return {
            "name": twin_data.get("name", twin_data["$dtId"]),
            "type": twin_data.get("type", "unknown"),
            "status": twin_data.get("status", "unknown"),
            "current_location": twin_data.get("current_zone", "unknown"),
            "battery_level": twin_data.get("battery_level", 100.0),
            "capabilities": twin_data.get("capabilities", []),
            "current_tasks": twin_data.get("current_tasks", []),
            "maintenance_status": twin_data.get("maintenance_status", "good"),
            "sensor_data": twin_data.get("sensor_data", {}),
            "operational_constraints": self._generate_robot_constraints(twin_data),
            "optimal_tasks": self._determine_robot_optimal_tasks(twin_data),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    def _extract_cottage_knowledge(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract cottage-specific knowledge"""
        return {
            "name": twin_data.get("name", twin_data["$dtId"]),
            "type": twin_data.get("type", "residential"),
            "square_footage": twin_data.get("square_footage", 0),
            "construction_year": twin_data.get("construction_year", 2020),
            "zones": twin_data.get("zones", []),
            "total_robots": twin_data.get("total_robots", 0),
            "current_occupancy": twin_data.get("current_occupancy", 0),
            "environmental_systems": twin_data.get("environmental_systems", {}),
            "security_systems": twin_data.get("security_systems", {}),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    def _extract_generic_knowledge(self, twin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract generic knowledge from any twin"""
        return {
            "id": twin_data["$dtId"],
            "type": twin_data.get("$metadata", {}).get("$model", "unknown"),
            "properties": {k: v for k, v in twin_data.items() 
                          if not k.startswith("$") and k != "metadata"},
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_constraints_from_conditions(self, twin_data: Dict[str, Any]) -> List[str]:
        """Generate constraints based on current conditions"""
        constraints = []
        
        # Temperature constraints
        temp = twin_data.get("temperature", 20.0)
        if temp > 30.0:
            constraints.append("high_temperature_limit_robot_operation")
        elif temp < 5.0:
            constraints.append("low_temperature_battery_consideration")
        
        # Humidity constraints
        humidity = twin_data.get("humidity", 50.0)
        if humidity > 80.0:
            constraints.append("high_humidity_electronics_caution")
        
        # Occupancy constraints
        occupancy = twin_data.get("occupancy", 0)
        if occupancy > 0:
            constraints.append("respect_human_presence")
            constraints.append("minimize_noise_disruption")
        
        # Lighting constraints
        lighting = twin_data.get("lighting_level", 500)
        if lighting < 200:
            constraints.append("low_lighting_use_robot_lighting")
        elif lighting > 1000:
            constraints.append("bright_lighting_camera_adjustment")
        
        return constraints
    
    def _determine_optimal_tasks(self, twin_data: Dict[str, Any]) -> List[str]:
        """Determine optimal tasks based on current conditions"""
        optimal_tasks = []
        
        # Temperature-based tasks
        temp = twin_data.get("temperature", 20.0)
        if 18.0 <= temp <= 26.0:
            optimal_tasks.append("inspection")
            optimal_tasks.append("cleaning")
        
        # Occupancy-based tasks
        occupancy = twin_data.get("occupancy", 0)
        if occupancy == 0:
            optimal_tasks.append("deep_cleaning")
            optimal_tasks.append("maintenance")
        elif occupancy > 0:
            optimal_tasks.append("quiet_assistance")
            optimal_tasks.append("non_disruptive_tasks")
        
        # Lighting-based tasks
        lighting = twin_data.get("lighting_level", 500)
        if lighting >= 300:
            optimal_tasks.append("visual_inspection")
            optimal_tasks.append("qr_code_scanning")
        
        return optimal_tasks
    
    def _generate_robot_constraints(self, twin_data: Dict[str, Any]) -> List[str]:
        """Generate robot operational constraints"""
        constraints = []
        
        # Battery constraints
        battery = twin_data.get("battery_level", 100.0)
        if battery < 20.0:
            constraints.append("low_battery_return_to_charge")
        elif battery < 50.0:
            constraints.append("moderate_battery_limit_heavy_tasks")
        
        # Maintenance constraints
        maintenance = twin_data.get("maintenance_status", "good")
        if maintenance != "good":
            constraints.append("maintenance_required_limit_operations")
        
        # Location constraints
        location = twin_data.get("current_zone", "unknown")
        if location == "charging_station":
            constraints.append("currently_charging")
        
        return constraints
    
    def _determine_robot_optimal_tasks(self, twin_data: Dict[str, Any]) -> List[str]:
        """Determine optimal tasks for robot based on current state"""
        optimal_tasks = []
        
        # Battery-based tasks
        battery = twin_data.get("battery_level", 100.0)
        if battery > 70.0:
            optimal_tasks.extend(["heavy_transport", "extended_patrol", "deep_cleaning"])
        elif battery > 30.0:
            optimal_tasks.extend(["inspection", "light_transport", "assistance"])
        else:
            optimal_tasks.append("return_to_charge")
        
        # Location-based tasks
        location = twin_data.get("current_zone", "unknown")
        if location == "kitchen":
            optimal_tasks.extend(["food_preparation_assist", "kitchen_inspection"])
        elif location == "living_room":
            optimal_tasks.extend(["tidying", "guest_assistance"])
        
        # Capability-based tasks
        capabilities = twin_data.get("capabilities", [])
        if "qr_scanning" in capabilities:
            optimal_tasks.append("qr_code_inspection")
        if "heavy_lift" in capabilities:
            optimal_tasks.append("heavy_transport")
        
        return optimal_tasks


class DigitalTwinRAGUpdater:
    """Update RAG with real-time Digital Twin data"""
    
    def __init__(self, rag_system: MultiTenantRAG, adt_client: DigitalTwinsClient):
        self.rag_system = rag_system
        self.adt_client = adt_client
    
    async def on_telemetry_update(self, twin_id: str, telemetry: Dict[str, Any]):
        """Handle real-time telemetry updates"""
        try:
            # 1. Get current twin state
            twin_state = await self._get_digital_twin(twin_id)
            
            # 2. Update RAG with new state
            twin_type = twin_state.get("$metadata", {}).get("$model", "")
            
            if "Zone" in twin_type:
                await self._update_zone_rag_document(twin_id, twin_state, telemetry)
            elif "Robot" in twin_type:
                await self._update_robot_rag_document(twin_id, twin_state, telemetry)
            
            print(f"✅ Updated RAG document for {twin_id} with new telemetry")
            
        except Exception as e:
            print(f"❌ Failed to update RAG for {twin_id}: {e}")
    
    async def _get_digital_twin(self, twin_id: str) -> Dict[str, Any]:
        """Get Digital Twin data"""
        loop = asyncio.get_event_loop()
        twin_data = await loop.run_in_executor(
            None, 
            self.adt_client.get_digital_twin, 
            twin_id
        )
        return twin_data
    
    async def _update_zone_rag_document(self, twin_id: str, twin_state: Dict[str, Any], telemetry: Dict[str, Any]):
        """Update zone knowledge with real-time data"""
        
        # Create enhanced zone document
        enhanced_zone = {
            "name": twin_state.get("name"),
            "type": twin_state.get("type"),
            "current_conditions": {
                "temperature": telemetry.get("temperature", twin_state.get("temperature", 20.0)),
                "humidity": telemetry.get("humidity", twin_state.get("humidity", 50.0)),
                "occupancy": telemetry.get("occupancy", twin_state.get("occupancy", 0)),
                "lighting": telemetry.get("lighting_level", twin_state.get("lighting_level", 500)),
                "noise_level": telemetry.get("noise_level", twin_state.get("noise_level", 40))
            },
            "real_time_constraints": self._generate_constraints_from_conditions(telemetry),
            "optimal_tasks": self._determine_optimal_tasks(telemetry),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        # Update RAG document
        await self.rag_system.update_document(
            client_id="cot_12345678",  # TODO: Get from context
            document_id=f"digital_twin_{twin_id}",
            content=json.dumps(enhanced_zone),
            metadata_update={
                "last_sync": datetime.now(timezone.utc).isoformat(),
                "data_source": "digital_twin_realtime"
            }
        )
    
    async def _update_robot_rag_document(self, twin_id: str, twin_state: Dict[str, Any], telemetry: Dict[str, Any]):
        """Update robot knowledge with real-time data"""
        
        enhanced_robot = {
            "name": twin_state.get("name"),
            "type": twin_state.get("type"),
            "status": telemetry.get("status", twin_state.get("status", "unknown")),
            "current_location": telemetry.get("current_zone", twin_state.get("current_zone", "unknown")),
            "battery_level": telemetry.get("battery_level", twin_state.get("battery_level", 100.0)),
            "capabilities": twin_state.get("capabilities", []),
            "sensor_data": telemetry.get("sensor_data", {}),
            "operational_constraints": self._generate_robot_constraints(telemetry),
            "optimal_tasks": self._determine_robot_optimal_tasks(telemetry),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        # Update RAG document
        await self.rag_system.update_document(
            client_id="cot_12345678",  # TODO: Get from context
            document_id=f"digital_twin_{twin_id}",
            content=json.dumps(enhanced_robot),
            metadata_update={
                "last_sync": datetime.now(timezone.utc).isoformat(),
                "data_source": "digital_twin_realtime"
            }
        )
    
    def _generate_constraints_from_conditions(self, telemetry: Dict[str, Any]) -> List[str]:
        """Generate constraints based on telemetry data"""
        constraints = []
        
        temp = telemetry.get("temperature", 20.0)
        if temp > 30.0:
            constraints.append("high_temperature_limit_robot_operation")
        elif temp < 5.0:
            constraints.append("low_temperature_battery_consideration")
        
        occupancy = telemetry.get("occupancy", 0)
        if occupancy > 0:
            constraints.append("respect_human_presence")
        
        return constraints
    
    def _determine_optimal_tasks(self, telemetry: Dict[str, Any]) -> List[str]:
        """Determine optimal tasks based on telemetry"""
        optimal_tasks = []
        
        occupancy = telemetry.get("occupancy", 0)
        if occupancy == 0:
            optimal_tasks.append("deep_cleaning")
        
        lighting = telemetry.get("lighting_level", 500)
        if lighting >= 300:
            optimal_tasks.append("visual_inspection")
        
        return optimal_tasks
    
    def _generate_robot_constraints(self, telemetry: Dict[str, Any]) -> List[str]:
        """Generate robot constraints from telemetry"""
        constraints = []
        
        battery = telemetry.get("battery_level", 100.0)
        if battery < 20.0:
            constraints.append("low_battery_return_to_charge")
        
        return constraints
    
    def _determine_robot_optimal_tasks(self, telemetry: Dict[str, Any]) -> List[str]:
        """Determine optimal robot tasks from telemetry"""
        optimal_tasks = []
        
        battery = telemetry.get("battery_level", 100.0)
        if battery > 70.0:
            optimal_tasks.append("heavy_transport")
        elif battery < 30.0:
            optimal_tasks.append("return_to_charge")
        
        return optimal_tasks


class DigitalTwinEnhancedRAG:
    """RAG system enhanced with Digital Twin context"""
    
    def __init__(self, rag_system: MultiTenantRAG, adt_client: DigitalTwinsClient):
        self.rag_system = rag_system
        self.adt_client = adt_client
    
    async def search_with_digital_twin_context(self, client_id: str, query: str, limit: int = 5):
        """Search with Digital Twin real-time context"""
        
        # 1. Standard RAG search
        rag_results = await self.rag_system.search(client_id, query, limit)
        
        # 2. Get real-time Digital Twin data
        twin_context = await self._get_current_twin_context(client_id)
        
        # 3. Enhance results with Digital Twin data
        enhanced_results = []
        for result in rag_results:
            enhanced_result = await self._enhance_with_twin_data(result, twin_context)
            enhanced_results.append(enhanced_result)
        
        # 4. Re-rank based on current conditions
        ranked_results = self._rank_by_current_conditions(enhanced_results, twin_context)
        
        return ranked_results
    
    async def _get_current_twin_context(self, client_id: str):
        """Get current Digital Twin state"""
        if not self.adt_client:
            return {}
        
        try:
            # Get all relevant twins for this client
            twin_query = "SELECT * FROM DIGITALTWINS WHERE $dtId LIKE 'cot_%'"
            twins = await self._query_twins(twin_query)
            
            # Organize by type
            context = {
                "zones": {},
                "robots": {},
                "sensors": {},
                "conditions": {}
            }
            
            for twin in twins:
                twin_id = twin["$dtId"]
                twin_type = twin.get("$metadata", {}).get("$model", "")
                
                if "Zone" in twin_type:
                    context["zones"][twin_id] = {
                        "name": twin.get("name"),
                        "temperature": twin.get("temperature"),
                        "humidity": twin.get("humidity"),
                        "occupancy": twin.get("occupancy"),
                        "lighting_level": twin.get("lighting_level"),
                        "noise_level": twin.get("noise_level")
                    }
                elif "Robot" in twin_type:
                    context["robots"][twin_id] = {
                        "name": twin.get("name"),
                        "status": twin.get("status"),
                        "battery_level": twin.get("battery_level"),
                        "current_location": twin.get("current_zone"),
                        "capabilities": twin.get("capabilities", [])
                    }
            
            return context
            
        except Exception as e:
            print(f"⚠️  Failed to get Digital Twin context: {e}")
            return {}
    
    async def _query_twins(self, query: str):
        """Query Digital Twins"""
        loop = asyncio.get_event_loop()
        query_result = await loop.run_in_executor(
            None,
            self.adt_client.query_twins,
            query
        )
        return query_result
    
    async def _enhance_with_twin_data(self, result: Dict[str, Any], twin_context: Dict[str, Any]):
        """Enhance RAG result with Digital Twin data"""
        enhanced_result = result.copy()
        
        # Add current conditions to result
        enhanced_result["twin_context"] = twin_context
        
        # Add relevance score based on current conditions
        relevance_boost = self._calculate_relevance_boost(result, twin_context)
        enhanced_result["similarity_score"] = min(1.0, result.get("similarity_score", 0) + relevance_boost)
        
        return enhanced_result
    
    def _calculate_relevance_boost(self, result: Dict[str, Any], twin_context: Dict[str, Any]) -> float:
        """Calculate relevance boost based on current conditions"""
        boost = 0.0
        
        metadata = result.get("metadata", {})
        
        # Zone relevance boost
        if metadata.get("type") == "zone":
            zone_name = metadata.get("zone_name")
            if zone_name in twin_context.get("zones", {}):
                zone_data = twin_context["zones"][zone_name]
                
                # Boost if conditions are optimal for tasks
                if zone_data.get("occupancy", 0) == 0:
                    boost += 0.1  # Unoccupied zones are better for tasks
                
                if zone_data.get("lighting_level", 0) >= 300:
                    boost += 0.05  # Good lighting for visual tasks
        
        # Robot relevance boost
        elif metadata.get("type") == "robot":
            robot_name = metadata.get("robot_name")
            if robot_name in twin_context.get("robots", {}):
                robot_data = twin_context["robots"][robot_name]
                
                # Boost if robot is available
                if robot_data.get("status") == "available":
                    boost += 0.1
                
                # Boost if battery is good
                if robot_data.get("battery_level", 0) > 70:
                    boost += 0.05
        
        return boost
    
    def _rank_by_current_conditions(self, results: List[Dict[str, Any]], twin_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Re-rank results based on current conditions"""
        
        # Sort by enhanced similarity score
        ranked_results = sorted(
            results, 
            key=lambda x: x.get("similarity_score", 0), 
            reverse=True
        )
        
        return ranked_results


class EnhancedRAGWithDigitalTwin:
    """Main integration class for RAG with Digital Twin"""
    
    def __init__(self, rag_system: MultiTenantRAG, adt_endpoint: Optional[str] = None):
        self.rag_system = rag_system
        self.adt_endpoint = adt_endpoint
        
        # Initialize components
        self.dtw_integration = AzureDigitalTwinRAGIntegration(rag_system, adt_endpoint)
        self.enhanced_search = None
        
        if self.dtw_integration.adt_client:
            self.enhanced_search = DigitalTwinEnhancedRAG(rag_system, self.dtw_integration.adt_client)
            self.updater = DigitalTwinRAGUpdater(rag_system, self.dtw_integration.adt_client)
    
    async def initialize_integration(self, client_id: str):
        """Initialize Digital Twin integration with RAG"""
        if not self.dtw_integration.adt_client:
            print("⚠️  Azure Digital Twins not available - using standard RAG")
            return
        
        print("🔗 Initializing Azure Digital Twin integration...")
        
        # 1. Sync existing Digital Twins to RAG
        await self._sync_all_twins_to_rag(client_id)
        
        # 2. Setup real-time updates (if telemetry handlers are available)
        # await self._setup_telemetry_handlers()
        
        # 3. Create enhanced search capabilities
        if self.enhanced_search:
            self.search = self.enhanced_search.search_with_digital_twin_context
        
        print("✅ Azure Digital Twin integration initialized")
    
    async def _sync_all_twins_to_rag(self, client_id: str):
        """Initial sync of all Digital Twins to RAG"""
        if not self.dtw_integration.adt_client:
            return
        
        try:
            # Get all twins
            twin_query = "SELECT * FROM DIGITALTWINS WHERE $dtId LIKE 'cot_%'"
            twins = await self._query_twins(twin_query)
            
            print(f"🔄 Found {len(twins)} Digital Twins to sync")
            
            for twin in twins:
                await self.dtw_integration.sync_digital_twin_to_rag(client_id, twin["$dtId"])
            
            print("✅ All Digital Twins synced to RAG")
            
        except Exception as e:
            print(f"❌ Failed to sync Digital Twins: {e}")
    
    async def _query_twins(self, query: str):
        """Query Digital Twins"""
        loop = asyncio.get_event_loop()
        query_result = await loop.run_in_executor(
            None,
            self.dtw_integration.adt_client.query_twins,
            query
        )
        return query_result
    
    async def create_cottage_digital_twins(self, client_id: str):
        """Create Digital Twin representation of cottage"""
        if not self.dtw_integration.adt_client:
            print("⚠️  Azure Digital Twins not available")
            return
        
        print("🏠 Creating cottage Digital Twins...")
        
        try:
            # Create cottage twin
            cottage_twin = {
                "$dtId": "cottage_main",
                "$metadata": {"$model": "dtmi:cottage:Cottage;1"},
                "name": "Main Cottage",
                "type": "residential",
                "square_footage": 1500,
                "construction_year": 2020,
                "total_robots": 3,
                "current_occupancy": 0
            }
            
            await self._upsert_digital_twin("cottage_main", cottage_twin)
            
            # Create zone twins
            zones = [
                {"name": "kitchen", "type": "indoor", "temperature": 22.0, "humidity": 45.0, "occupancy": 0, "lighting_level": 800},
                {"name": "living_room", "type": "indoor", "temperature": 21.0, "humidity": 50.0, "occupancy": 1, "lighting_level": 600},
                {"name": "bedroom", "type": "indoor", "temperature": 20.0, "humidity": 55.0, "occupancy": 0, "lighting_level": 400},
                {"name": "bathroom", "type": "indoor", "temperature": 23.0, "humidity": 70.0, "occupancy": 0, "lighting_level": 700},
                {"name": "dock", "type": "outdoor", "temperature": 18.0, "humidity": 60.0, "occupancy": 0, "lighting_level": 1000},
                {"name": "garage", "type": "mixed", "temperature": 15.0, "humidity": 65.0, "occupancy": 0, "lighting_level": 500},
                {"name": "garden", "type": "outdoor", "temperature": 19.0, "humidity": 55.0, "occupancy": 0, "lighting_level": 1200}
            ]
            
            for zone in zones:
                zone_twin = {
                    "$dtId": f"zone_{zone['name']}",
                    "$metadata": {"$model": "dtmi:cottage:Zone;1"},
                    **zone,
                    "landmarks": self._get_zone_landmarks(zone["name"]),
                    "common_tasks": self._get_zone_tasks(zone["name"]),
                    "constraints": self._get_zone_constraints(zone["name"]),
                    "connectivity": self._get_zone_connectivity(zone["name"]),
                    "typical_items": self._get_zone_items(zone["name"])
                }
                
                await self._upsert_digital_twin(f"zone_{zone['name']}", zone_twin)
                
                # Create relationship
                relationship = {
                    "$relationshipId": f"cottage_has_{zone['name']}",
                    "$targetId": f"zone_{zone['name']}"
                }
                await self._create_relationship("cottage_main", f"cottage_has_{zone['name']}", relationship)
            
            # Create robot twins
            robots = [
                {"name": "Quadruped_001", "type": "quadruped", "status": "available", "battery_level": 85.0, "current_zone": "living_room"},
                {"name": "Humanoid_001", "type": "humanoid", "status": "available", "battery_level": 92.0, "current_zone": "charging_station"},
                {"name": "Drone_001", "type": "drone", "status": "charging", "battery_level": 45.0, "current_zone": "dock"}
            ]
            
            for robot in robots:
                robot_twin = {
                    "$dtId": f"robot_{robot['name'].lower()}",
                    "$metadata": {"$model": "dtmi:cottage:Robot;1"},
                    **robot,
                    "capabilities": self._get_robot_capabilities(robot["type"]),
                    "maintenance_status": "good",
                    "sensor_data": self._get_robot_sensor_data(robot["type"])
                }
                
                await self._upsert_digital_twin(f"robot_{robot['name'].lower()}", robot_twin)
                
                # Create relationship
                relationship = {
                    "$relationshipId": f"cottage_has_{robot['name'].lower()}",
                    "$targetId": f"robot_{robot['name'].lower()}"
                }
                await self._create_relationship("cottage_main", f"cottage_has_{robot['name'].lower()}", relationship)
            
            print("✅ Cottage Digital Twins created successfully")
            
            # Sync to RAG
            await self._sync_all_twins_to_rag(client_id)
            
        except Exception as e:
            print(f"❌ Failed to create cottage Digital Twins: {e}")
    
    async def _upsert_digital_twin(self, twin_id: str, twin_data: Dict[str, Any]):
        """Create or update Digital Twin"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.dtw_integration.adt_client.upsert_digital_twin,
            twin_id,
            twin_data
        )
    
    async def _create_relationship(self, source_twin: str, relationship_id: str, relationship: Dict[str, Any]):
        """Create relationship between twins"""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.dtw_integration.adt_client.create_or_update_relationship,
                source_twin,
                relationship_id,
                relationship
            )
        except Exception as e:
            print(f"⚠️  Failed to create relationship {relationship_id}: {e}")
    
    def _get_zone_landmarks(self, zone_name: str) -> List[str]:
        """Get landmarks for zone"""
        landmarks_map = {
            "kitchen": ["refrigerator", "stove", "sink", "dishwasher", "microwave", "coffee_maker", "dining_table"],
            "living_room": ["sofa", "tv_stand", "coffee_table", "bookshelf", "fireplace", "entertainment_center"],
            "bedroom": ["bed", "wardrobe", "dresser", "nightstand", "desk", "mirror", "closet"],
            "bathroom": ["toilet", "sink", "shower", "bathtub", "medicine_cabinet", "mirror", "towel_rack"],
            "dock": ["loading_bay", "storage_shed", "outdoor_faucet", "security_camera", "motion_lights"],
            "garage": ["workbench", "tool_chest", "vehicle_space", "storage_racks", "charging_station"],
            "garden": ["garden_beds", "watering_system", "tool_shed", "compost_bin", "greenhouse", "pathways"]
        }
        return landmarks_map.get(zone_name, [])
    
    def _get_zone_tasks(self, zone_name: str) -> List[str]:
        """Get common tasks for zone"""
        tasks_map = {
            "kitchen": ["food_preparation", "cooking", "cleaning", "dishwashing", "inventory_check", "food_organization"],
            "living_room": ["tidying", "dusting", "vacuuming", "item_retrieval", "guest_assistance", "entertainment_setup"],
            "bedroom": ["bed_making", "clothing_organization", "cleaning", "laundry_assistance", "item_delivery"],
            "bathroom": ["cleaning", "supply_replacement", "spill_cleanup", "maintenance_check", "inventory_check"],
            "dock": ["package_handling", "outdoor_cleaning", "yard_maintenance", "security_patrol", "equipment_storage"],
            "garage": ["vehicle_assistance", "tool_organization", "maintenance", "storage_management", "charging_management"],
            "garden": ["plant_care", "watering", "weeding", "harvesting", "lawn_maintenance", "seasonal_planting"]
        }
        return tasks_map.get(zone_name, [])
    
    def _get_zone_constraints(self, zone_name: str) -> List[str]:
        """Get constraints for zone"""
        constraints_map = {
            "kitchen": ["no_liquid_spills_near_electronics", "keep_appliances_clear", "temperature_control_for_perishables"],
            "living_room": ["keep_walkways_clear", "quiet_operation_during_movies", "protect_electronics"],
            "bedroom": ["maintain_privacy", "quiet_operation", "respect_personal_space"],
            "bathroom": ["water_safety", "slip_prevention", "ventilation", "chemical_safety"],
            "dock": ["weather_considerations", "security_awareness", "proper_weight_distribution"],
            "garage": ["vehicle_safety", "tool_organization", "adequate_lighting", "fire_safety"],
            "garden": ["plant_safety", "water_conservation", "weather_monitoring", "pest_control"]
        }
        return constraints_map.get(zone_name, [])
    
    def _get_zone_connectivity(self, zone_name: str) -> List[str]:
        """Get connectivity for zone"""
        connectivity_map = {
            "kitchen": ["living_room", "dining_area", "pantry"],
            "living_room": ["kitchen", "bedroom", "entrance", "hallway"],
            "bedroom": ["bathroom", "living_room", "closet"],
            "bathroom": ["bedroom", "hallway"],
            "dock": ["garage", "garden", "entrance"],
            "garage": ["house", "dock", "yard"],
            "garden": ["house", "garage", "dock"]
        }
        return connectivity_map.get(zone_name, [])
    
    def _get_zone_items(self, zone_name: str) -> List[str]:
        """Get typical items for zone"""
        items_map = {
            "kitchen": ["groceries", "cookware", "dishes", "small_appliances", "cleaning_supplies"],
            "living_room": ["remote_controls", "magazines", "blankets", "decorative_items", "electronics"],
            "bedroom": ["clothing", "bedding", "personal_items", "books", "electronics"],
            "bathroom": ["toiletries", "towels", "cleaning_supplies", "medications", "first_aid"],
            "dock": ["packages", "outdoor_equipment", "tools", "garden_supplies", "seasonal_items"],
            "garage": ["vehicles", "tools", "equipment", "supplies", "maintenance_items"],
            "garden": ["plants", "tools", "seeds", "fertilizer", "garden_equipment", "harvest_baskets"]
        }
        return items_map.get(zone_name, [])
    
    def _get_robot_capabilities(self, robot_type: str) -> List[str]:
        """Get capabilities for robot type"""
        capabilities_map = {
            "quadruped": ["outdoor_navigation", "rough_terrain_handling", "payload_transport", "qr_scanning", "patrol"],
            "humanoid": ["fine_manipulation", "object_recognition", "qr_scanning", "cleaning", "assistance"],
            "drone": ["aerial_surveillance", "qr_scanning", "photography", "inspection", "delivery"]
        }
        return capabilities_map.get(robot_type, [])
    
    def _get_robot_sensor_data(self, robot_type: str) -> Dict[str, Any]:
        """Get sensor data for robot type"""
        sensor_map = {
            "quadruped": {"camera": True, "lidar": True, "gyroscope": True, "accelerometer": True},
            "humanoid": {"camera": True, "microphone": True, "touch_sensors": True, "gyroscope": True},
            "drone": {"camera": True, "gps": True, "altimeter": True, "accelerometer": True}
        }
        return sensor_map.get(robot_type, {})
