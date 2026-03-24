"""
Context-Aware AI Intent Service with Memory System

This service builds and maintains contextual knowledge about the cottage environment
through user interactions, enabling increasingly sophisticated intent understanding.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .domain import ClarificationQuestion, MissionConstraint, MissionIntent
from .openai_intent import OpenAIIntentService

# Memory storage path
MEMORY_PATH = Path("data/ai_memory.json")


class ContextualMemory:
    """Persistent memory system for AI context building."""
    
    def __init__(self, memory_path: Path = MEMORY_PATH):
        self.memory_path = memory_path
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load existing memory or create initial structure."""
        if self.memory_path.exists():
            try:
                with open(self.memory_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Initial cottage context
        return {
            "version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "cottage_context": {
                "zones": [
                    {
                        "name": "kitchen",
                        "type": "indoor",
                        "description": "Main kitchen area with counters, appliances, and dining table",
                        "common_tasks": ["food_preparation", "cleaning", "dishwashing", "inventory_check"],
                        "landmarks": ["refrigerator", "stove", "sink", "dining_table", "coffee_machine"],
                        "constraints": ["no_liquid_spills", "keep_counters_clear"]
                    },
                    {
                        "name": "living_room",
                        "type": "indoor", 
                        "description": "Living area with seating, entertainment center, and fireplace",
                        "common_tasks": ["tidying", "dust_collection", "item_retrieval", "guest_assistance"],
                        "landmarks": ["sofa", "tv_stand", "coffee_table", "bookshelf", "fireplace"],
                        "constraints": ["avoid_obstructing_walkways", "quiet_operation_preferred"]
                    },
                    {
                        "name": "bedroom",
                        "type": "indoor",
                        "description": "Master bedroom with bed, wardrobe, and desk",
                        "common_tasks": ["bed_making", "clothing_organization", "cleaning", "item_delivery"],
                        "landmarks": ["bed", "wardrobe", "desk", "nightstand", "dresser"],
                        "constraints": ["maintain_privacy", "quiet_hours_10pm_7am"]
                    },
                    {
                        "name": "bathroom",
                        "type": "indoor",
                        "description": "Bathroom with shower, sink, and toilet",
                        "common_tasks": ["cleaning", "towel_replacement", "supply_check", "spill_cleanup"],
                        "landmarks": ["shower", "sink", "toilet", "medicine_cabinet", "towel_rack"],
                        "constraints": ["water_sensitive_equipment", "slippery_when_wet"]
                    },
                    {
                        "name": "dock",
                        "type": "outdoor",
                        "description": "Loading dock area for deliveries and outdoor storage",
                        "common_tasks": ["package_handling", "outdoor_cleaning", "yard_maintenance", "security_patrol"],
                        "landmarks": ["loading_bay", "storage_shed", "garage_door", "outdoor_faucet", "security_camera"],
                        "constraints": ["weather_exposure", "security_conscious", "heavy_load_capacity"]
                    },
                    {
                        "name": "garage",
                        "type": "mixed",
                        "description": "Garage space for vehicles and tools",
                        "common_tasks": ["vehicle_assistance", "tool_organization", "maintenance", "storage_management"],
                        "landmarks": ["workbench", "tool_chest", "vehicle_space", "storage_racks", "charging_station"],
                        "constraints": ["vehicle_safety", "tool_organization_required", "adequate_lighting"]
                    },
                    {
                        "name": "garden",
                        "type": "outdoor",
                        "description": "Garden area with plants and pathways",
                        "common_tasks": ["plant_care", "path_maintenance", "weed_control", "harvest_assistance"],
                        "landmarks": ["garden_bed", "watering_system", "tool_shed", "compost_bin", "greenhouse"],
                        "constraints": ["plant_sensitive_operations", "weather_dependent", "path_clearance"]
                    }
                ],
                "robot_capabilities": {
                    "quadruped": {
                        "strengths": ["outdoor_navigation", "rough_terrain", "payload_transport", "stair_climbing"],
                        "limitations": ["fine_manipulation", "indoor_narrow_spaces", "quiet_operation"],
                        "preferred_tasks": ["outdoor_delivery", "patrol", "heavy_transport", "terrain_inspection"]
                    },
                    "humanoid": {
                        "strengths": ["fine_manipulation", "indoor_navigation", "human_interaction", "tool_use"],
                        "limitations": ["payload_capacity", "outdoor_rough_terrain", "battery_life"],
                        "preferred_tasks": ["object_manipulation", "indoor_assistance", "tool_operation", "human_interaction"]
                    },
                    "cargo": {
                        "strengths": ["heavy_payload", "large_cargo_space", "stability", "long_range"],
                        "limitations": ["fine_manipulation", "indoor_narrow_spaces", "stair_navigation"],
                        "preferred_tasks": ["bulk_transport", "supply_delivery", "waste_collection", "equipment_moving"]
                    },
                    "drone": {
                        "strengths": ["aerial_surveillance", "quick_inspection", "area_mapping", "delivery"],
                        "limitations": ["payload_weight", "indoor_operation", "battery_life", "weather_sensitivity"],
                        "preferred_tasks": ["aerial_inspection", "area_survey", "quick_delivery", "security_patrol"]
                    }
                },
                "common_items": {
                    "groceries": {
                        "typical_locations": ["kitchen_refrigerator", "kitchen_counters", "dock_loading_bay"],
                        "handling_requirements": ["temperature_control", "careful_handling", "separation_by_type"],
                        "common_destinations": ["kitchen", "refrigerator", "pantry"]
                    },
                    "packages": {
                        "typical_locations": ["dock", "front_door", "garage"],
                        "handling_requirements": ["careful_handling", "recipient_verification", "damage_inspection"],
                        "common_destinations": ["living_room", "bedroom", "office"]
                    },
                    "tools": {
                        "typical_locations": ["garage_workbench", "tool_chest", "storage_shed"],
                        "handling_requirements": ["proper_storage", "maintenance_check", "safety_inspection"],
                        "common_destinations": ["work_area", "maintenance_location", "storage_location"]
                    },
                    "cleaning_supplies": {
                        "typical_locations": ["bathroom_cabinet", "cleaning_closet", "kitchen_under_sink"],
                        "handling_requirements": ["segregated_storage", "accessibility", "inventory_tracking"],
                        "common_destinations": ["cleaning_area", "storage_location", "usage_location"]
                    }
                },
                "user_preferences": {
                    "default_priorities": {
                        "safety_related": "urgent",
                        "food_related": "high", 
                        "cleaning": "normal",
                        "organization": "low",
                        "entertainment": "low"
                    },
                    "time_preferences": {
                        "quiet_hours": {"start": "22:00", "end": "07:00"},
                        "preferred_delivery_times": ["10:00-12:00", "14:00-16:00"],
                        "cleaning_windows": ["09:00-11:00", "15:00-17:00"]
                    },
                    "interaction_patterns": {
                        "frequent_requests": ["kitchen_assistance", "living_room_tidying", "package_handling"],
                        "clarification_needs": ["specific_locations", "timing_preferences", "priority_levels"],
                        "success_indicators": ["task_completion_confirmation", "photo_updates", "status_notifications"]
                    }
                }
            },
            "interaction_history": [],
            "learned_patterns": {
                "frequent_missions": {},
                "user_specific_terms": {},
                "contextual_clarifications": {},
                "success_patterns": {},
                "failure_patterns": {}
            },
            "adaptations": {
                "zone_aliases": {},
                "task_shortcuts": {},
                "preference_adjustments": {},
                "capability_assumptions": {}
            }
        }
    
    def _save_memory(self) -> None:
        """Save current memory state to disk."""
        self._memory["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        with open(self.memory_path, 'w') as f:
            json.dump(self._memory, f, indent=2, default=str)
    
    def add_interaction(self, request: str, intent: MissionIntent, result: Dict[str, Any]) -> None:
        """Record a new interaction for learning."""
        interaction = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request": request,
            "intent": intent.to_dict(),
            "result": result,
            "context_extracted": self._extract_context_from_interaction(request, intent, result)
        }
        
        self._memory["interaction_history"].append(interaction)
        self._update_learned_patterns(interaction)
        self._save_memory()
    
    def _extract_context_from_interaction(self, request: str, intent: MissionIntent, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contextual information from interaction."""
        context = {
            "mentioned_zones": [],
            "mentioned_items": [],
            "mission_type": intent.mission_type,
            "success": result.get("success", False),
            "clarifications_needed": result.get("clarifications", []),
            "user_terms": []
        }
        
        # Extract zones from request
        for zone in self._memory["cottage_context"]["zones"]:
            if zone["name"].lower() in request.lower():
                context["mentioned_zones"].append(zone["name"])
        
        # Extract items from request
        for item_name in self._memory["cottage_context"]["common_items"]:
            if item_name.lower() in request.lower():
                context["mentioned_items"].append(item_name)
        
        # Extract user-specific terms
        words = request.lower().split()
        for word in words:
            if len(word) > 3 and word not in ["the", "and", "for", "with", "from", "to", "in", "at", "on"]:
                context["user_terms"].append(word)
        
        return context
    
    def _update_learned_patterns(self, interaction: Dict[str, Any]) -> None:
        """Update learned patterns from new interaction."""
        context = interaction["context_extracted"]
        mission_type = context["mission_type"]
        
        # Update frequent missions
        if mission_type not in self._memory["learned_patterns"]["frequent_missions"]:
            self._memory["learned_patterns"]["frequent_missions"][mission_type] = 0
        self._memory["learned_patterns"]["frequent_missions"][mission_type] += 1
        
        # Update user-specific terms
        for term in context["user_terms"]:
            if term not in self._memory["learned_patterns"]["user_specific_terms"]:
                self._memory["learned_patterns"]["user_specific_terms"][term] = {"count": 0, "contexts": []}
            self._memory["learned_patterns"]["user_specific_terms"][term]["count"] += 1
            self._memory["learned_patterns"]["user_specific_terms"][term]["contexts"].append(context)
        
        # Update success/failure patterns
        if context["success"]:
            if mission_type not in self._memory["learned_patterns"]["success_patterns"]:
                self._memory["learned_patterns"]["success_patterns"][mission_type] = []
            self._memory["learned_patterns"]["success_patterns"][mission_type].append(context)
        else:
            if mission_type not in self._memory["learned_patterns"]["failure_patterns"]:
                self._memory["learned_patterns"]["failure_patterns"][mission_type] = []
            self._memory["learned_patterns"]["failure_patterns"][mission_type].append(context)
    
    def get_enhanced_context(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get enhanced context including learned patterns."""
        context = self._memory["cottage_context"].copy()
        
        # Add learned patterns
        context["learned_patterns"] = self._memory["learned_patterns"]
        
        # Add adaptations
        context["adaptations"] = self._memory["adaptations"]
        
        # Add recent interactions (last 10)
        context["recent_interactions"] = self._memory["interaction_history"][-10:]
        
        return context
    
    def get_zone_info(self, zone_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific zone."""
        for zone in self._memory["cottage_context"]["zones"]:
            if zone["name"].lower() == zone_name.lower():
                return zone
        return None
    
    def get_item_info(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific item."""
        for item_key, item_info in self._memory["cottage_context"]["common_items"].items():
            if item_key.lower() == item_name.lower():
                return item_info
        return None
    
    def add_zone_alias(self, alias: str, actual_zone: str) -> None:
        """Add a user-specific zone alias."""
        self._memory["adaptations"]["zone_aliases"][alias.lower()] = actual_zone
        self._save_memory()
    
    def add_task_shortcut(self, shortcut: str, full_task: str) -> None:
        """Add a user-specific task shortcut."""
        self._memory["adaptations"]["task_shortcuts"][shortcut.lower()] = full_task
        self._save_memory()


class ContextualIntentService:
    """Enhanced intent service with contextual memory."""
    
    def __init__(self, known_zones: List[str], fallback: Any, memory: Optional[ContextualMemory] = None):
        self._known_zones = known_zones
        self._fallback = fallback
        self._memory = memory or ContextualMemory()
        self._openai_service = OpenAIIntentService(known_zones, fallback)
    
    @property
    def enabled(self) -> bool:
        return self._openai_service.enabled
    
    @property
    def provider_label(self) -> str:
        return f"contextual-{self._openai_service.provider_label}"
    
    def parse_request(
        self,
        request_text: str,
        *,
        requested_by: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> MissionIntent | ClarificationQuestion:
        """Parse request with enhanced contextual understanding."""
        
        # Get enhanced context
        enhanced_context = self._memory.get_enhanced_context(requested_by)
        
        # Pre-process request to resolve aliases and shortcuts
        processed_request = self._preprocess_request(request_text)
        
        # Merge provided context with enhanced context
        merged_context = {**(context or {}), **enhanced_context}
        
        # Add cottage-specific system prompt
        contextual_prompt = self._build_contextual_prompt(processed_request, merged_context)
        
        # Parse using enhanced context
        try:
            result = self._parse_with_context(processed_request, contextual_prompt, requested_by, merged_context)
            
            # Record interaction for learning
            self._memory.add_interaction(
                request=request_text,
                intent=result if isinstance(result, MissionIntent) else None,
                result={"success": isinstance(result, MissionIntent), "clarifications": [] if isinstance(result, MissionIntent) else [result.prompt]}
            )
            
            return result
            
        except Exception as e:
            # Fallback to basic parsing
            fallback_result = self._fallback.parse_request(
                processed_request, 
                requested_by=requested_by, 
                context=merged_context
            )
            
            # Record failed interaction
            self._memory.add_interaction(
                request=request_text,
                intent=fallback_result if isinstance(fallback_result, MissionIntent) else None,
                result={"success": False, "error": str(e)}
            )
            
            return fallback_result
    
    def _preprocess_request(self, request_text: str) -> str:
        """Pre-process request to resolve aliases and shortcuts."""
        processed = request_text.lower()
        
        # Resolve zone aliases
        for alias, actual_zone in self._memory._memory["adaptations"]["zone_aliases"].items():
            processed = processed.replace(alias, actual_zone)
        
        # Resolve task shortcuts
        for shortcut, full_task in self._memory._memory["adaptations"]["task_shortcuts"].items():
            processed = processed.replace(shortcut, full_task)
        
        return processed
    
    def _build_contextual_prompt(self, request: str, context: Dict[str, Any]) -> str:
        """Build enhanced system prompt with cottage context."""
        base_prompt = self._openai_service.SYSTEM_PROMPT
        
        contextual_additions = f"""
        
COTTAGE CONTEXT:
You are operating in a residential cottage environment with the following zones:
{self._format_zones_for_prompt(context.get('zones', []))}

Available robot types and their capabilities:
{self._format_robot_capabilities_for_prompt(context.get('robot_capabilities', {}))}

Common items and their typical locations:
{self._format_items_for_prompt(context.get('common_items', {}))}

User preferences and patterns:
{self._format_preferences_for_prompt(context.get('user_preferences', {}))}

Recent successful missions:
{self._format_recent_successes(context.get('recent_interactions', []))}

LEARNED PATTERNS:
{self._format_learned_patterns(context.get('learned_patterns', {}))}

Use this contextual knowledge to:
1. Better understand user intent and terminology
2. Make intelligent assumptions about missing information
3. Provide more relevant clarifications
4. Suggest appropriate robot assignments
5. Consider user preferences and past patterns

Always prioritize safety and respect the residential environment.
"""
        
        return base_prompt + contextual_additions
    
    def _format_zones_for_prompt(self, zones: List[Dict[str, Any]]) -> str:
        """Format zone information for prompt."""
        zone_info = []
        for zone in zones:
            zone_info.append(f"- {zone['name']}: {zone['description']} (type: {zone['type']})")
            zone_info.append(f"  Common tasks: {', '.join(zone['common_tasks'])}")
            zone_info.append(f"  Landmarks: {', '.join(zone['landmarks'])}")
            zone_info.append(f"  Constraints: {', '.join(zone['constraints'])}")
        return "\n".join(zone_info)
    
    def _format_robot_capabilities_for_prompt(self, capabilities: Dict[str, Any]) -> str:
        """Format robot capabilities for prompt."""
        cap_info = []
        for robot_type, details in capabilities.items():
            cap_info.append(f"- {robot_type}:")
            cap_info.append(f"  Strengths: {', '.join(details['strengths'])}")
            cap_info.append(f"  Limitations: {', '.join(details['limitations'])}")
            cap_info.append(f"  Preferred tasks: {', '.join(details['preferred_tasks'])}")
        return "\n".join(cap_info)
    
    def _format_items_for_prompt(self, items: Dict[str, Any]) -> str:
        """Format common items for prompt."""
        item_info = []
        for item_name, details in items.items():
            item_info.append(f"- {item_name}:")
            item_info.append(f"  Typical locations: {', '.join(details['typical_locations'])}")
            item_info.append(f"  Handling requirements: {', '.join(details['handling_requirements'])}")
            item_info.append(f"  Common destinations: {', '.join(details['common_destinations'])}")
        return "\n".join(item_info)
    
    def _format_preferences_for_prompt(self, preferences: Dict[str, Any]) -> str:
        """Format user preferences for prompt."""
        pref_info = []
        pref_info.append(f"- Default priorities: {preferences['default_priorities']}")
        pref_info.append(f"- Time preferences: {preferences['time_preferences']}")
        pref_info.append(f"- Interaction patterns: {preferences['interaction_patterns']}")
        return "\n".join(pref_info)
    
    def _format_recent_successes(self, interactions: List[Dict[str, Any]]) -> str:
        """Format recent successful interactions for prompt."""
        successes = [i for i in interactions if i.get("result", {}).get("success", False)][-5:]  # Last 5 successes
        success_info = []
        for interaction in successes:
            success_info.append(f"- '{interaction['request']}' → {interaction['intent']['mission_type']} (success)")
        return "\n".join(success_info) if success_info else "No recent successful missions recorded."
    
    def _format_learned_patterns(self, patterns: Dict[str, Any]) -> str:
        """Format learned patterns for prompt."""
        pattern_info = []
        
        if patterns.get("frequent_missions"):
            frequent = sorted(patterns["frequent_missions"].items(), key=lambda x: x[1], reverse=True)[:3]
            pattern_info.append(f"- Frequent mission types: {', '.join([f'{mt} ({count})' for mt, count in frequent])}")
        
        if patterns.get("user_specific_terms"):
            terms = sorted(patterns["user_specific_terms"].items(), key=lambda x: x[1]["count"], reverse=True)[:5]
            pattern_info.append(f"- User terminology: {', '.join([f'{term} ({details[\"count\"]} uses)' for term, details in terms])}")
        
        return "\n".join(pattern_info) if pattern_info else "No significant patterns learned yet."
    
    def _parse_with_context(
        self, 
        request: str, 
        contextual_prompt: str, 
        requested_by: str, 
        context: Dict[str, Any]
    ) -> MissionIntent | ClarificationQuestion:
        """Parse request using contextual prompt."""
        # This would integrate with the OpenAI service using the enhanced prompt
        # For now, we'll use the existing service with context enhancement
        
        # In a full implementation, this would call OpenAI with the contextual prompt
        # For now, fallback to existing service with enhanced context
        return self._openai_service.parse_request(
            request, 
            requested_by=requested_by, 
            context=context
        )
    
    def learn_from_feedback(self, mission_id: str, feedback: Dict[str, Any]) -> None:
        """Learn from mission execution feedback."""
        # Update memory based on execution results
        adaptations = self._memory._memory["adaptations"]
        
        # Learn from successful patterns
        if feedback.get("success"):
            # Reinforce successful approaches
            pass
        
        # Learn from failures
        if not feedback.get("success"):
            # Adjust assumptions and patterns
            pass
        
        self._memory._save_memory()
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of learned memory."""
        memory = self._memory._memory
        return {
            "total_interactions": len(memory["interaction_history"]),
            "learned_zones": len(memory["adaptations"]["zone_aliases"]),
            "learned_shortcuts": len(memory["adaptations"]["task_shortcuts"]),
            "frequent_missions": memory["learned_patterns"]["frequent_missions"],
            "user_terms": list(memory["learned_patterns"]["user_specific_terms"].keys())[:10],
            "last_updated": memory["updated_at"]
        }
