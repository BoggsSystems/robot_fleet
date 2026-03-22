"""
Enhanced RAG system integration with dynamic fleet database.
"""

from __future__ import annotations

import json
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List

from .multi_tenant_rag import MultiTenantRAG
from .fleet_database import fleet_manager, fleet_context_provider


class DynamicFleetRAG:
    """RAG system enhanced with dynamic fleet data"""
    
    def __init__(self, rag_system: MultiTenantRAG):
        self.rag_system = rag_system
        self.fleet_context_provider = fleet_context_provider
    
    async def search_with_fleet_context(self, client_id: str, query: str, limit: int = 5):
        """Enhanced RAG search with real-time fleet context"""
        
        # 1. Get real-time fleet context
        fleet_context = await self.fleet_context_provider.get_fleet_context("cottage_fleet")
        
        # 2. Perform standard RAG search
        rag_results = await self.rag_system.search(client_id, query, limit)
        
        # 3. Enhance results with fleet data
        enhanced_results = []
        for result in rag_results:
            enhanced_result = await self._enhance_result_with_fleet_data(result, fleet_context)
            enhanced_results.append(enhanced_result)
        
        # 4. Re-rank based on fleet availability
        ranked_results = self._rank_by_fleet_availability(enhanced_results, fleet_context)
        
        return ranked_results
    
    async def _enhance_result_with_fleet_data(self, result: Dict[str, Any], fleet_context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance individual RAG result with fleet context"""
        
        enhanced_result = result.copy()
        metadata = result.get("metadata", {})
        
        # Add fleet context
        enhanced_result["fleet_context"] = {
            "available_robots": len(fleet_context.get("available_robots", [])),
            "busy_robots": len(fleet_context.get("busy_robots", [])),
            "charging_robots": len(fleet_context.get("charging_robots", [])),
            "total_robots": fleet_context.get("fleet_status", {}).get("total_count", 0)
        }
        
        # Calculate relevance boost based on fleet availability
        relevance_boost = 0.0
        
        if metadata.get("type") == "robot":
            robot_type = metadata.get("robot_type")
            
            # Check if robots of this type are available
            available_of_type = [
                r for r in fleet_context.get("available_robots", [])
                if r.get("type") == robot_type
            ]
            
            if available_of_type:
                relevance_boost += 0.2
                enhanced_result["available_robots_of_type"] = len(available_of_type)
                enhanced_result["robot_availability"] = "high"
            else:
                relevance_boost -= 0.1
                enhanced_result["available_robots_of_type"] = 0
                enhanced_result["robot_availability"] = "low"
        
        elif metadata.get("type") == "zone":
            zone_name = metadata.get("zone_name")
            
            # Check if robots are available for this zone
            available_robots = fleet_context.get("available_robots", [])
            suitable_robots = [
                r for r in available_robots
                if self._is_robot_suitable_for_zone(r, zone_name)
            ]
            
            if suitable_robots:
                relevance_boost += 0.15
                enhanced_result["suitable_robots_available"] = len(suitable_robots)
                enhanced_result["zone_robot_availability"] = "good"
            else:
                relevance_boost -= 0.05
                enhanced_result["suitable_robots_available"] = 0
                enhanced_result["zone_robot_availability"] = "poor"
        
        # Update similarity score
        enhanced_result["similarity_score"] = min(1.0, result.get("similarity_score", 0) + relevance_boost)
        enhanced_result["relevance_boost"] = relevance_boost
        
        # Add real-time considerations
        enhanced_result["real_time_considerations"] = self._generate_fleet_considerations(
            metadata, fleet_context
        )
        
        return enhanced_result
    
    def _is_robot_suitable_for_zone(self, robot: Dict[str, Any], zone_name: str) -> bool:
        """Check if robot is suitable for zone"""
        robot_type = robot.get("type", "")
        capabilities = robot.get("capabilities", [])
        
        # Zone suitability rules
        zone_suitability = {
            "kitchen": ["humanoid"],  # Fine manipulation needed
            "dock": ["quadruped"],    # Heavy lifting, outdoor
            "garage": ["quadruped"],   # Heavy lifting, mixed environment
            "garden": ["quadruped"],   # Outdoor, rough terrain
            "living_room": ["humanoid", "quadruped"],  # General assistance
            "bedroom": ["humanoid"],    # Privacy, fine manipulation
            "bathroom": ["humanoid"]   # Small space, careful manipulation
        }
        
        suitable_types = zone_suitability.get(zone_name, ["humanoid", "quadruped"])
        return robot_type in suitable_types
    
    def _generate_fleet_considerations(self, metadata: Dict[str, Any], fleet_context: Dict[str, Any]) -> List[str]:
        """Generate real-time fleet considerations"""
        considerations = []
        
        available_count = len(fleet_context.get("available_robots", []))
        busy_count = len(fleet_context.get("busy_robots", []))
        total_count = fleet_context.get("fleet_status", {}).get("total_count", 0)
        
        if metadata.get("type") == "mission":
            mission_type = metadata.get("mission_type", "")
            
            if available_count == 0:
                considerations.append("No robots currently available - all robots busy or charging")
            elif available_count < 2:
                considerations.append(f"Limited robot availability - only {available_count} robots available")
            
            if mission_type in ["transport", "heavy_lift"]:
                quadrupeds = [
                    r for r in fleet_context.get("available_robots", [])
                    if r.get("type") == "quadruped"
                ]
                if not quadrupeds:
                    considerations.append("No quadruped robots available for heavy lifting tasks")
            
            if mission_type in ["cleaning", "assistance"]:
                humanoids = [
                    r for r in fleet_context.get("available_robots", [])
                    if r.get("type") == "humanoid"
                ]
                if not humanoids:
                    considerations.append("No humanoid robots available for fine manipulation tasks")
        
        elif metadata.get("type") == "zone":
            zone_name = metadata.get("zone_name", "")
            
            if zone_name == "dock":
                available_quadrupeds = [
                    r for r in fleet_context.get("available_robots", [])
                    if r.get("type") == "quadruped"
                ]
                if not available_quadrupeds:
                    considerations.append("No quadruped robots available for dock operations")
            
            elif zone_name == "kitchen":
                available_humanoids = [
                    r for r in fleet_context.get("available_robots", [])
                    if r.get("type") == "humanoid"
                ]
                if not available_humanoids:
                    considerations.append("No humanoid robots available for kitchen tasks")
        
        # Battery considerations
        available_robots = fleet_context.get("available_robots", [])
        low_battery_robots = [
            r for r in available_robots
            if r.get("battery_level", 100) < 30
        ]
        
        if low_battery_robots:
            considerations.append(
                f"{len(low_battery_robots)} available robots have low battery (<30%)"
            )
        
        return considerations
    
    def _rank_by_fleet_availability(self, results: List[Dict[str, Any]], fleet_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Re-rank results based on fleet availability"""
        
        # Sort by enhanced similarity score first
        sorted_results = sorted(
            results,
            key=lambda x: x.get("similarity_score", 0),
            reverse=True
        )
        
        # Apply additional ranking based on fleet status
        available_count = len(fleet_context.get("available_robots", []))
        
        for result in sorted_results:
            metadata = result.get("metadata", {})
            
            # Boost results that are feasible with current fleet
            if metadata.get("type") == "mission":
                mission_type = metadata.get("mission_type", "")
                
                if mission_type in ["transport", "heavy_lift"] and available_count >= 1:
                    result["feasibility_score"] = 1.0
                elif mission_type in ["cleaning", "assistance"] and available_count >= 1:
                    result["feasibility_score"] = 1.0
                else:
                    result["feasibility_score"] = 0.5
            
            elif metadata.get("type") == "robot":
                robot_type = metadata.get("robot_type", "")
                available_of_type = result.get("available_robots_of_type", 0)
                
                if available_of_type > 0:
                    result["feasibility_score"] = 1.0
                else:
                    result["feasibility_score"] = 0.0
            
            elif metadata.get("type") == "zone":
                suitable_robots = result.get("suitable_robots_available", 0)
                
                if suitable_robots > 0:
                    result["feasibility_score"] = 1.0
                else:
                    result["feasibility_score"] = 0.0
        
        return sorted_results
    
    async def sync_fleet_data_to_rag(self, client_id: str):
        """Sync current fleet data to RAG documents"""
        
        # Get current fleet context
        fleet_context = await self.fleet_context_provider.get_fleet_context("cottage_fleet")
        
        # Create fleet status document
        fleet_doc = {
            "id": "fleet_status_current",
            "content": json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "fleet_status": fleet_context.get("fleet_status", {}),
                "available_robots": fleet_context.get("available_robots", []),
                "busy_robots": fleet_context.get("busy_robots", []),
                "charging_robots": fleet_context.get("charging_robots", []),
                "maintenance_robots": fleet_context.get("maintenance_robots", [])
            }),
            "metadata": {
                "type": "fleet_status",
                "category": "real_time",
                "scope": "client_specific",
                "last_sync": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Add to RAG
        await self.rag_system.add_document(
            client_id=client_id,
            document=fleet_doc
        )
        
        # Create individual robot documents
        for robot_id, robot_info in fleet_context.get("robots", {}).items():
            robot_doc = {
                "id": f"robot_current_{robot_id}",
                "content": json.dumps({
                    "robot_id": robot_id,
                    "name": robot_info.get("name"),
                    "type": robot_info.get("type"),
                    "status": robot_info.get("status"),
                    "battery_level": robot_info.get("battery_level"),
                    "current_location": robot_info.get("current_location"),
                    "current_task": robot_info.get("current_task"),
                    "capabilities": robot_info.get("capabilities"),
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }),
                "metadata": {
                    "type": "robot_state",
                    "category": "real_time",
                    "robot_id": robot_id,
                    "scope": "client_specific",
                    "last_sync": datetime.now(timezone.utc).isoformat()
                }
            }
            
            await self.rag_system.add_document(
                client_id=client_id,
                document=robot_doc
            )
        
        print(f"✅ Synced fleet data to RAG for client {client_id}")
    
    async def get_fleet_recommendations(self, client_id: str, mission_type: str) -> List[Dict[str, Any]]:
        """Get fleet-based recommendations for mission type"""
        
        fleet_context = await self.fleet_context_provider.get_fleet_context("cottage_fleet")
        available_robots = fleet_context.get("available_robots", [])
        
        recommendations = []
        
        if mission_type in ["transport", "heavy_lift"]:
            # Recommend quadrupeds for heavy tasks
            quadrupeds = [
                r for r in available_robots
                if r.get("type") == "quadruped" and r.get("battery_level", 0) > 30
            ]
            
            if quadrupeds:
                recommendations.append({
                    "mission_type": mission_type,
                    "recommended_robots": quadrupeds[:2],  # Top 2
                    "rationale": "Quadruped robots have heavy lift capability and sufficient battery",
                    "confidence": 0.9
                })
        
        elif mission_type in ["cleaning", "assistance"]:
            # Recommend humanoids for fine manipulation
            humanoids = [
                r for r in available_robots
                if r.get("type") == "humanoid" and r.get("battery_level", 0) > 30
            ]
            
            if humanoids:
                recommendations.append({
                    "mission_type": mission_type,
                    "recommended_robots": humanoids[:2],  # Top 2
                    "rationale": "Humanoid robots have fine manipulation capabilities and sufficient battery",
                    "confidence": 0.9
                })
        
        elif mission_type in ["inspection", "surveillance"]:
            # Recommend drones or any available robot
            drones = [
                r for r in available_robots
                if r.get("type") == "drone" and r.get("battery_level", 0) > 20
            ]
            
            if drones:
                recommendations.append({
                    "mission_type": mission_type,
                    "recommended_robots": drones[:1],  # Top drone
                    "rationale": "Drone provides aerial perspective for inspection tasks",
                    "confidence": 0.85
                })
            elif available_robots:
                # Fallback to any available robot
                recommendations.append({
                    "mission_type": mission_type,
                    "recommended_robots": available_robots[:2],
                    "rationale": "Available robots can perform inspection with ground-level capabilities",
                    "confidence": 0.7
                })
        
        return recommendations


# Initialize dynamic fleet RAG
dynamic_fleet_rag = None


async def initialize_dynamic_fleet_rag(rag_system: MultiTenantRAG):
    """Initialize dynamic fleet RAG integration"""
    global dynamic_fleet_rag
    
    # Setup fleet database
    from .fleet_database import setup_fleet_database
    await setup_fleet_database()
    
    # Initialize dynamic fleet RAG
    dynamic_fleet_rag = DynamicFleetRAG(rag_system)
    
    print("🚀 Dynamic Fleet RAG integration initialized")
    return dynamic_fleet_rag
