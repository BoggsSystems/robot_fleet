"""
Enhanced intent service with Azure Digital Twin integration.
"""

from __future__ import annotations

import json
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .contextual_intent import ContextualIntentService, MissionIntent
from .multi_tenant_rag import MultiTenantRAG
from .azure_digital_twin_rag import EnhancedRAGWithDigitalTwin
from .dynamic_fleet_rag import dynamic_fleet_rag, initialize_dynamic_fleet_rag


class DigitalTwinEnhancedIntentService:
    """Intent service enhanced with Azure Digital Twin real-time data"""
    
    def __init__(self, rag_system, adt_endpoint: Optional[str] = None):
        self.rag_system = rag_system
        self.adt_endpoint = adt_endpoint
        
        # Initialize Digital Twin integration
        self.dtw_integration = EnhancedRAGWithDigitalTwin(rag_system, adt_endpoint)
        
        # Initialize dynamic fleet RAG
        self.dynamic_fleet_rag = None
        
        # Initialize base intent service
        self.base_intent_service = ContextualIntentService()
        
        # Override search method with Digital Twin enhanced version
        if self.dtw_integration.enhanced_search:
            self.base_intent_service.rag_system.search = self.dtw_integration.enhanced_search.search_with_digital_twin_context
    
    async def initialize(self, client_id: str):
        """Initialize Digital Twin enhanced intent service"""
        print("🧠 Initializing Digital Twin Enhanced Intent Service...")
        
        # Initialize Digital Twin integration
        await self.dtw_integration.initialize_integration(client_id)
        
        # Initialize dynamic fleet RAG
        self.dynamic_fleet_rag = await initialize_dynamic_fleet_rag(self.rag_system)
        
        # Override search method with enhanced version
        if self.dtw_integration.enhanced_search:
            self.base_intent_service.rag_system.search = self.dtw_integration.enhanced_search.search_with_digital_twin_context
        
        # Also override with dynamic fleet context
        if self.dynamic_fleet_rag:
            original_search = self.base_intent_service.rag_system.search
            self.base_intent_service.rag_system.search = self._enhanced_search_with_all_context
        
        print("✅ Digital Twin Enhanced Intent Service initialized")
    
    async def _enhanced_search_with_all_context(self, client_id: str, query: str, limit: int = 5):
        """Enhanced search combining Digital Twin and dynamic fleet context"""
        
        # 1. Get Digital Twin context
        twin_context = await self._get_real_time_context(client_id)
        
        # 2. Get dynamic fleet context  
        fleet_context = await self.dynamic_fleet_rag.get_fleet_context("cottage_fleet")
        
        # 3. Perform standard RAG search
        rag_results = await self.rag_system.search(client_id, query, limit)
        
        # 4. Enhance with both contexts
        enhanced_results = []
        for result in rag_results:
            enhanced_result = await self._enhance_with_all_context(result, twin_context, fleet_context)
            enhanced_results.append(enhanced_result)
        
        # 5. Re-rank based on all conditions
        ranked_results = self._rank_by_all_conditions(enhanced_results, twin_context, fleet_context)
        
        return ranked_results
    
    async def _enhance_with_all_context(self, result: Dict[str, Any], twin_context: Dict[str, Any], fleet_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance result with both Digital Twin and fleet context"""
        
        enhanced_result = result.copy()
        metadata = result.get("metadata", {})
        
        # Add combined context
        enhanced_result["combined_context"] = {
            "digital_twin": {
                "zones": twin_context.get("zones", {}),
                "robots": twin_context.get("robots", {}),
                "environmental": twin_context.get("environmental", {})
            },
            "fleet": {
                "available_count": len(fleet_context.get("available_robots", [])),
                "busy_count": len(fleet_context.get("busy_robots", [])),
                "charging_count": len(fleet_context.get("charging_robots", [])),
                "total_robots": fleet_context.get("fleet_status", {}).get("total_count", 0)
            }
        }
        
        # Calculate combined relevance boost
        relevance_boost = 0.0
        
        if metadata.get("type") == "robot":
            robot_type = metadata.get("robot_type")
            
            # Check Digital Twin availability
            dt_robots = twin_context.get("robots", {})
            if robot_type in dt_robots:
                dt_robot = dt_robots[robot_type]
                if dt_robot.get("status") == "available":
                    relevance_boost += 0.1
            
            # Check fleet availability
            available_robots = fleet_context.get("available_robots", [])
            fleet_available = [
                r for r in available_robots
                if r.get("type") == robot_type
            ]
            
            if fleet_available:
                relevance_boost += 0.2
                enhanced_result["robot_availability"] = "high"
            else:
                enhanced_result["robot_availability"] = "low"
        
        elif metadata.get("type") == "mission":
            mission_type = metadata.get("mission_type", "")
            available_count = len(fleet_context.get("available_robots", []))
            
            if available_count >= 2:
                relevance_boost += 0.15
                enhanced_result["mission_feasibility"] = "high"
            elif available_count >= 1:
                relevance_boost += 0.1
                enhanced_result["mission_feasibility"] = "medium"
            else:
                relevance_boost -= 0.1
                enhanced_result["mission_feasibility"] = "low"
        
        # Update similarity score
        enhanced_result["similarity_score"] = min(1.0, result.get("similarity_score", 0) + relevance_boost)
        enhanced_result["relevance_boost"] = relevance_boost
        
        # Generate combined considerations
        enhanced_result["combined_considerations"] = self._generate_combined_considerations(
            metadata, twin_context, fleet_context
        )
        
        return enhanced_result
    
    def _generate_combined_considerations(self, metadata: Dict[str, Any], twin_context: Dict[str, Any], fleet_context: Dict[str, Any]) -> List[str]:
        """Generate considerations from both Digital Twin and fleet data"""
        
        considerations = []
        
        # Digital Twin considerations
        zones = twin_context.get("zones", {})
        if metadata.get("zone_name") in zones:
            zone_data = zones[metadata["zone_name"]]
            
            if zone_data.get("occupancy", 0) > 0:
                considerations.append(f"Zone {metadata['zone_name']} currently occupied - respect human presence")
            else:
                considerations.append(f"Zone {metadata['zone_name']} unoccupied - optimal for tasks")
        
        # Fleet considerations
        available_count = len(fleet_context.get("available_robots", []))
        if available_count == 0:
            considerations.append("No robots currently available in fleet")
        elif available_count < 2:
            considerations.append(f"Limited fleet availability - only {available_count} robots available")
        
        # Combined considerations
        if metadata.get("mission_type") == "heavy_lift":
            quadrupeds = [
                r for r in fleet_context.get("available_robots", [])
                if r.get("type") == "quadruped"
            ]
            if not quadrupeds:
                considerations.append("No quadruped robots available for heavy lifting - consider alternative approaches")
        
        return considerations
    
    def _rank_by_all_conditions(self, results: List[Dict[str, Any]], twin_context: Dict[str, Any], fleet_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank results based on both Digital Twin and fleet conditions"""
        
        # Calculate overall feasibility score
        for result in results:
            metadata = result.get("metadata", {})
            
            feasibility_score = 0.5  # Base score
            
            # Digital Twin feasibility
            if metadata.get("type") == "zone":
                zone_name = metadata.get("zone_name")
                zones = twin_context.get("zones", {})
                
                if zone_name in zones:
                    zone_data = zones[zone_name]
                    
                    # Good conditions boost
                    if zone_data.get("occupancy", 0) == 0:
                        feasibility_score += 0.2
                    if zone_data.get("lighting_level", 0) > 300:
                        feasibility_score += 0.1
            
            # Fleet feasibility
            available_count = len(fleet_context.get("available_robots", []))
            if available_count >= 1:
                feasibility_score += 0.2
            
            result["feasibility_score"] = min(1.0, feasibility_score)
        
        # Sort by combined score (similarity + feasibility)
        return sorted(
            results,
            key=lambda x: (x.get("similarity_score", 0) + x.get("feasibility_score", 0)),
            reverse=True
        )
        async def parse_request(self, request_text: str, requested_by: str, context: dict = None) -> MissionIntent:
        """
        Parse user request with both Digital Twin and dynamic fleet context.
        """
        # Get client ID
        client_id = self._get_client_id(requested_by)
        
        # Search with enhanced RAG (Digital Twin + Fleet)
        if hasattr(self, '_enhanced_search_with_all_context'):
            rag_results = await self._enhanced_search_with_all_context(client_id, request_text, limit=5)
        
        # Get real-time Digital Twin context
        twin_context = await self._get_real_time_context(client_id)
        
        # Get dynamic fleet context
        fleet_context = await self.dynamic_fleet_rag.get_fleet_context("cottage_fleet") if self.dynamic_fleet_rag else {}
        
        # Build enhanced prompt with combined context
        enhanced_prompt = self._build_combined_enhanced_prompt(
            query=request_text,
            rag_context=rag_results,
            twin_context=twin_context,
            fleet_context=fleet_context,
            user_context=context,
            client_id=client_id
        )
        
        # Parse with AI
        parsed_intent = await self._parse_with_llm(enhanced_prompt, request_text)
        
        # Enhance intent with real-time considerations
        enhanced_intent = self._enhance_intent_with_real_time_data(parsed_intent, twin_context)
        
        # Learn from interaction
        await self._learn_from_interaction(request_text, enhanced_intent, rag_results, twin_context, client_id)
        
        return enhanced_intent
    
    def _get_client_id(self, requested_by: str) -> str:
        """Get client ID from requested_by string"""
        # Extract client ID from requested_by (e.g., "user@cot_12345678" -> "cot_12345678")
        if "@" in requested_by:
            return requested_by.split("@")[1]
        return "cot_12345678"  # Default cottage client
    
    async def _get_real_time_context(self, client_id: str) -> Dict[str, Any]:
        """Get real-time Digital Twin context"""
        if not self.dtw_integration.enhanced_search:
            return {}
        
        try:
            twin_context = await self.dtw_integration.enhanced_search._get_current_twin_context(client_id)
            return twin_context
        except Exception as e:
            print(f"⚠️  Failed to get real-time context: {e}")
            return {}
    
        mission_templates = [r for r in rag_context if r["metadata"].get("type") == "mission"]
        
        # Get current conditions from Digital Twin
        current_conditions = twin_context.get("zones", {})
        current_robot_states = twin_context.get("robots", {})
        
        prompt = f"""
DIGITAL TWIN ENHANCED COTTAGE CONTEXT:

CURRENT ENVIRONMENTAL CONDITIONS:
{json.dumps(current_conditions, indent=2)}

CURRENT ROBOT STATES:
{json.dumps(current_robot_states, indent=2)}

STATIC COTTAGE KNOWLEDGE:
ZONES:
{json.dumps([json.loads(r["content"]) for r in cottage_knowledge], indent=2)}

ROBOT CAPABILITIES:
{json.dumps([json.loads(r["content"]) for r in robot_knowledge], indent=2)}

MISSION TEMPLATES:
{json.dumps([json.loads(r["content"]) for r in mission_templates], indent=2)}

USER CONTEXT:
{json.dumps(user_context or {}, indent=2)}

USER REQUEST: {query}

Using both static knowledge and real-time Digital Twin data, parse the user's intent into a structured mission plan.

CRITICAL CONSIDERATIONS:
1. Current environmental conditions (temperature, humidity, occupancy, lighting)
2. Robot availability and current states (battery, location, status)
3. Zone-specific constraints based on current conditions
4. Optimal timing and resource allocation
5. Real-time safety considerations

Return a structured mission intent with:
- mission_type (inspection, transport, cleaning, assistance)
- objective (clear description of goal)
- source_zone and destination_zone
- required_capabilities
- priority
- constraints (including real-time constraints)
- real_time_considerations (based on current conditions)
- optimal_execution_time (if applicable)
- confidence_score (0.0-1.0)
"""
        return prompt
    
    async def _parse_with_llm(self, enhanced_prompt: str, request_text: str) -> MissionIntent:
        """Parse with LLM using enhanced prompt"""
        # Use the base intent service's parsing with enhanced prompt
        try:
            # This would integrate with OpenAI/LLM service
            # For now, return a mock enhanced intent
            return self._create_mock_enhanced_intent(request_text)
        except Exception as e:
            print(f"❌ Failed to parse with LLM: {e}")
            # Fallback to basic intent parsing
            return self._create_basic_intent(request_text)
    
    def _create_mock_enhanced_intent(self, request_text: str) -> MissionIntent:
        """Create mock enhanced intent for demonstration"""
        # Extract basic intent from request
        request_lower = request_text.lower()
        
        if "scan" in request_lower and "kitchen" in request_lower:
            return MissionIntent(
                mission_id=f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                mission_type="inspection",
                objective="Scan kitchen area for QR codes and report findings",
                source_zone="kitchen",
                destination_zone="kitchen",
                required_capabilities=["inspection", "qr_scanning"],
                priority="normal",
                constraints=["respect_current_occupancy", "optimal_lighting_required"],
                real_time_considerations=[
                    "Kitchen currently unoccupied - optimal for scanning",
                    "Good lighting conditions (800 lux) - suitable for QR scanning",
                    "Quadruped robot available with 85% battery in adjacent living room"
                ],
                optimal_execution_time="immediate",
                confidence_score=0.92,
                requested_by="user@ios_app"
            )
        else:
            return self._create_basic_intent(request_text)
    
    def _create_basic_intent(self, request_text: str) -> MissionIntent:
        """Create basic intent as fallback"""
        return MissionIntent(
            mission_id=f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            mission_type="assistance",
            objective=request_text,
            source_zone="unknown",
            destination_zone="unknown",
            required_capabilities=["basic_assistance"],
            priority="normal",
            constraints=[],
            real_time_considerations=[],
            optimal_execution_time="asap",
            confidence_score=0.5,
            requested_by="user@ios_app"
        )
    
    def _enhance_intent_with_real_time_data(self, intent: MissionIntent, twin_context: dict) -> MissionIntent:
        """Enhance parsed intent with real-time Digital Twin and fleet data"""
        
        # Get fleet context
        fleet_context = {}
        if hasattr(self, 'dynamic_fleet_rag') and self.dynamic_fleet_rag:
            fleet_context = await self.dynamic_fleet_rag.get_fleet_context("cottage_fleet")
        
        # Add real-time considerations from both sources
        real_time_considerations = []
        
        # Digital Twin considerations
        zones = twin_context.get("zones", {})
        if intent.source_zone in zones:
            zone_data = zones[intent.source_zone]
            
            if zone_data.get("occupancy", 0) > 0:
                real_time_considerations.append(f"{intent.source_zone} currently occupied by {zone_data['occupancy']} people - use quiet operation")
            else:
                real_time_considerations.append(f"{intent.source_zone} currently unoccupied - optimal for tasks")
            
            # Environmental considerations
            temp = zone_data.get("temperature", 20.0)
            if temp > 30.0:
                real_time_considerations.append(f"High temperature ({temp}°C) - limit robot operation duration")
            elif temp < 5.0:
                real_time_considerations.append(f"Low temperature ({temp}°C) - consider battery performance")
            
            lighting = zone_data.get("lighting_level", 0)
            if lighting < 200:
                real_time_considerations.append("Low lighting - robot lighting required")
                if "robot_lighting" not in intent.required_capabilities:
                    intent.required_capabilities.append("robot_lighting")
        
        # Fleet considerations
        available_robots = fleet_context.get("available_robots", [])
        if len(available_robots) == 0:
            real_time_considerations.append("No robots currently available - mission queued until resources available")
        elif len(available_robots) < 2:
            real_time_considerations.append(f"Limited robot availability - only {len(available_robots)} robots available")
        
        # Robot-specific considerations
        if intent.required_capabilities:
            suitable_robots = [
                r for r in available_robots
                if any(cap in r.get("capabilities", []) for cap in intent.required_capabilities)
            ]
            
            if not suitable_robots:
                real_time_considerations.append("No available robots have required capabilities - consider alternative approaches")
            else:
                # Add battery considerations
                low_battery_robots = [
                    r for r in suitable_robots
                    if r.get("battery_level", 100) < 30
                ]
                
                if low_battery_robots:
                    real_time_considerations.append(f"{len(low_battery_robots)} suitable robots have low battery (<30%)")
        
        # Update intent
        intent.real_time_considerations = real_time_considerations
        
        # Adjust confidence based on availability
        if len(available_robots) >= 2:
            intent.confidence_score = min(1.0, intent.confidence_score + 0.1)
        elif len(available_robots) >= 1:
            intent.confidence_score = min(1.0, intent.confidence_score + 0.05)
        else:
            intent.confidence_score = max(0.0, intent.confidence_score - 0.2)
        
        # Add fleet feasibility
        intent.fleet_feasibility = "high" if len(available_robots) >= 2 else "medium" if len(available_robots) >= 1 else "low"
        
        return intent
        """Enhance parsed intent with real-time Digital Twin data"""
        
        # Get zone conditions
        zones = twin_context.get("zones", {})
        robots = twin_context.get("robots", {})
        
        # Add real-time considerations
        real_time_considerations = []
        
        if intent.source_zone in zones:
            zone_data = zones[intent.source_zone]
            
            # Occupancy considerations
            occupancy = zone_data.get("occupancy", 0)
            if occupancy > 0:
                real_time_considerations.append(f"Zone currently occupied by {occupancy} people - use quiet operation")
            else:
                real_time_considerations.append("Zone currently unoccupied - optimal for tasks")
            
            # Lighting considerations
            lighting = zone_data.get("lighting_level", 0)
            if lighting < 200:
                real_time_considerations.append("Low lighting - robot lighting required")
                intent.required_capabilities.append("robot_lighting")
            elif lighting >= 300:
                real_time_considerations.append(f"Good lighting conditions ({lighting} lux) - suitable for visual tasks")
            
            # Temperature considerations
            temp = zone_data.get("temperature", 20.0)
            if temp > 30.0:
                real_time_considerations.append(f"High temperature ({temp}°C) - limit robot operation duration")
                intent.constraints.append("high_temperature_limit_duration")
            
            # Add constraints based on conditions
            if occupancy > 0:
                intent.constraints.append("quiet_operation")
            if lighting < 200:
                intent.constraints.append("require_robot_lighting")
        
        # Add robot availability considerations
        available_robots = [r for r in robots.values() if r.get("status") == "available"]
        if available_robots:
            best_robot = max(available_robots, key=lambda x: x.get("battery_level", 0))
            real_time_considerations.append(
                f"Best available robot: {best_robot.get('name')} with {best_robot.get('battery_level', 0)}% battery"
            )
            intent.confidence_score = min(1.0, intent.confidence_score + 0.1)
        else:
            real_time_considerations.append("No robots currently available")
            intent.confidence_score = max(0.0, intent.confidence_score - 0.2)
        
        # Update real-time considerations
        intent.real_time_considerations = real_time_considerations
        
        return intent
    
    async def _learn_from_interaction(self, request: str, intent: MissionIntent, rag_results: list, 
                                    twin_context: dict, client_id: str):
        """Learn from user interaction with Digital Twin context"""
        
        # Record interaction with Digital Twin context
        interaction = {
            "request": request,
            "intent": intent.dict(),
            "rag_results_used": [r.get("id") for r in rag_results],
            "twin_context": twin_context,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client_id": client_id
        }
        
        # Store interaction for learning
        await self._store_interaction_with_context(interaction)
        
        # Update user patterns with real-time considerations
        await self._update_user_patterns_with_context(interaction)
    
    async def _store_interaction_with_context(self, interaction: dict):
        """Store interaction with Digital Twin context"""
        # This would store in the learning database
        # For now, just print the interaction
        print(f"📚 Stored interaction with Digital Twin context: {interaction['request']}")
    
    async def _update_user_patterns_with_context(self, interaction: dict):
        """Update user patterns with Digital Twin context"""
        # This would update the learning patterns
        # For now, just acknowledge the update
        print(f"🧠 Updated user patterns with Digital Twin context")
    
    async def get_real_time_mission_recommendations(self, client_id: str) -> List[Dict[str, Any]]:
        """Get real-time mission recommendations based on Digital Twin data"""
        
        twin_context = await self._get_real_time_context(client_id)
        recommendations = []
        
        # Analyze current conditions and suggest optimal missions
        zones = twin_context.get("zones", {})
        robots = twin_context.get("robots", {})
        
        for zone_id, zone_data in zones.items():
            zone_recommendations = []
            
            # Check occupancy
            if zone_data.get("occupancy", 0) == 0:
                zone_recommendations.append({
                    "mission_type": "deep_cleaning",
                    "reason": "Zone unoccupied - optimal for deep cleaning",
                    "confidence": 0.9
                })
            
            # Check lighting
            lighting = zone_data.get("lighting_level", 0)
            if lighting >= 300:
                zone_recommendations.append({
                    "mission_type": "inspection",
                    "reason": f"Good lighting conditions ({lighting} lux)",
                    "confidence": 0.85
                })
            
            # Check for available robots
            available_robots = [r for r in robots.values() if r.get("status") == "available"]
            if available_robots:
                best_robot = max(available_robots, key=lambda x: x.get("battery_level", 0))
                
                recommendations.append({
                    "zone": zone_id,
                    "zone_name": zone_data.get("name", zone_id),
                    "recommended_missions": zone_recommendations,
                    "best_robot": {
                        "name": best_robot.get("name"),
                        "battery_level": best_robot.get("battery_level"),
                        "capabilities": best_robot.get("capabilities", [])
                    },
                    "overall_confidence": sum(r["confidence"] for r in zone_recommendations) / len(zone_recommendations) if zone_recommendations else 0.0
                })
        
        # Sort by overall confidence
        recommendations.sort(key=lambda x: x["overall_confidence"], reverse=True)
        
        return recommendations
    
    async def simulate_telemetry_update(self, twin_id: str, telemetry: Dict[str, Any]):
        """Simulate telemetry update for testing"""
        if hasattr(self.dtw_integration, 'updater'):
            await self.dtw_integration.updater.on_telemetry_update(twin_id, telemetry)
            print(f"📡 Simulated telemetry update for {twin_id}: {telemetry}")


# Factory function for easy initialization
async def create_digital_twin_enhanced_intent_service(rag_system, adt_endpoint: Optional[str] = None, 
                                                     client_id: str = "cot_12345678") -> DigitalTwinEnhancedIntentService:
    """Create and initialize Digital Twin enhanced intent service"""
    service = DigitalTwinEnhancedIntentService(rag_system, adt_endpoint)
    await service.initialize(client_id)
    return service
