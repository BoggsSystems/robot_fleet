# Contextual AI System for Cottage Fleet Management

## Overview

This system creates an **AI that learns and remembers** about your cottage environment, building contextual knowledge through interactions to provide increasingly sophisticated mission understanding.

## 🧠 **Core Components**

### **1. ContextualMemory** (`contextual_intent.py`)
- **Persistent memory storage** in `data/ai_memory.json`
- **Initial cottage context** with zones, robot capabilities, and common items
- **Interaction history tracking** with pattern learning
- **User preference adaptation** over time

### **2. ContextualIntentService** (`contextual_intent.py`)
- **Enhanced intent parsing** with contextual understanding
- **Learning from user interactions** and feedback
- **Alias resolution** for user-specific terminology
- **Progressive pattern recognition**

### **3. ContextualMissionBrain** (`contextual_integration.py`)
- **Integration layer** with existing mission planning
- **Feedback learning** from mission execution
- **User knowledge management** and adaptation

## 🏠 **Initial Cottage Context**

### **Zone Knowledge**
```json
{
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
    }
    // ... more zones
  ]
}
```

### **Robot Capabilities**
```json
{
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
    }
    // ... more robot types
  }
}
```

### **Common Items & Patterns**
```json
{
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
    }
  },
  "user_preferences": {
    "default_priorities": {
      "safety_related": "urgent",
      "food_related": "high", 
      "cleaning": "normal",
      "organization": "low"
    },
    "time_preferences": {
      "quiet_hours": {"start": "22:00", "end": "07:00"},
      "preferred_delivery_times": ["10:00-12:00", "14:00-16:00"]
    }
  }
}
```

## 🔄 **Learning Progression**

### **First Interaction**
```
User: "Check the kitchen for groceries and bring them to the living room"

AI Learning:
- Learns "kitchen" and "living room" are important zones
- Associates "groceries" with kitchen → living room transfer
- Records cargo_transfer mission type
- Notes successful completion pattern
```

### **Second Interaction**
```
User: "Scan the kitchen area"

AI Context:
- Knows "kitchen" from previous interaction
- Understands "scan" = inspection mission type
- Suggests appropriate robot (quadruped for inspection)
- Uses learned zone knowledge for routing
```

### **Third Interaction**
```
User: "Do a quick tidy in the living room"

AI Learning:
- Learns "quick tidy" = light cleaning task
- Associates with living_room zone
- Records user terminology preference
- Updates task shortcuts memory
```

### **Fourth Interaction**
```
User: "Do a stock check in the pantry"

AI Context:
- Uses learned alias: "pantry" → "kitchen"
- Understands "stock check" = inventory inspection
- Applies learned kitchen zone knowledge
- Suggests appropriate robot and timing
```

## 🧩 **Memory Building Process**

### **1. Context Extraction**
```python
def _extract_context_from_interaction(self, request: str, intent: MissionIntent, result: Dict[str, Any]) -> Dict[str, Any]:
    context = {
        "mentioned_zones": [],      # "kitchen", "living_room"
        "mentioned_items": [],      # "groceries", "packages"
        "mission_type": intent.mission_type,  # "cargo_transfer"
        "success": result.get("success", False),
        "clarifications_needed": result.get("clarifications", []),
        "user_terms": []           # "quick tidy", "stock check"
    }
```

### **2. Pattern Learning**
```python
def _update_learned_patterns(self, interaction: Dict[str, Any]) -> None:
    # Track frequent mission types
    self._memory["learned_patterns"]["frequent_missions"][mission_type] += 1
    
    # Learn user-specific terminology
    for term in context["user_terms"]:
        self._memory["learned_patterns"]["user_specific_terms"][term]["count"] += 1
    
    # Record success/failure patterns for future optimization
```

### **3. Adaptive System**
```python
def add_zone_alias(self, alias: str, actual_zone: str) -> None:
    """User: 'pantry' → AI learns it means 'kitchen'"""
    self._memory["adaptations"]["zone_aliases"][alias.lower()] = actual_zone

def add_task_shortcut(self, shortcut: str, full_task: str) -> None:
    """User: 'quick tidy' → AI learns it means 'light_cleaning_and_organization'"""
    self._memory["adaptations"]["task_shortcuts"][shortcut.lower()] = full_task
```

## 🎯 **Enhanced AI Prompting**

### **Contextual System Prompt**
```
COTTAGE CONTEXT:
You are operating in a residential cottage environment with the following zones:
- kitchen: Main kitchen area with counters, appliances, and dining table (type: indoor)
  Common tasks: food_preparation, cleaning, dishwashing, inventory_check
  Landmarks: refrigerator, stove, sink, dining_table, coffee_machine
  Constraints: no_liquid_spills, keep_counters_clear

Available robot types and their capabilities:
- quadruped:
  Strengths: outdoor_navigation, rough_terrain, payload_transport, stair_climbing
  Limitations: fine_manipulation, indoor_narrow_spaces, quiet_operation
  Preferred tasks: outdoor_delivery, patrol, heavy_transport, terrain_inspection

Common items and their typical locations:
- groceries:
  Typical locations: kitchen_refrigerator, kitchen_counters, dock_loading_bay
  Handling requirements: temperature_control, careful_handling, separation_by_type
  Common destinations: kitchen, refrigerator, pantry

User preferences and patterns:
- Default priorities: {"safety_related": "urgent", "food_related": "high"}
- Time preferences: {"quiet_hours": {"start": "22:00", "end": "07:00"}}

LEARNED PATTERNS:
- Frequent mission types: cargo_transfer (12), inspection (8), general_assistance (5)
- User terminology: quick tidy (3 uses), stock check (2 uses), scan area (4 uses)

Recent successful missions:
- 'Check the kitchen for groceries and bring them to the living room' → cargo_transfer (success)
- 'Scan the kitchen area' → inspection (success)
- 'Do a quick tidy in the living room' → general_assistance (success)

Use this contextual knowledge to:
1. Better understand user intent and terminology
2. Make intelligent assumptions about missing information
3. Provide more relevant clarifications
4. Suggest appropriate robot assignments
5. Consider user preferences and past patterns

Always prioritize safety and respect the residential environment.
```

## 📊 **Memory Evolution**

### **Initial State**
```json
{
  "total_interactions": 0,
  "learned_zones": 0,
  "learned_shortcuts": 0,
  "frequent_missions": {},
  "user_terms": [],
  "last_updated": "2024-03-20T16:00:00Z"
}
```

### **After 10 Interactions**
```json
{
  "total_interactions": 10,
  "learned_zones": 2,
  "learned_shortcuts": 3,
  "frequent_missions": {
    "cargo_transfer": 4,
    "inspection": 3,
    "general_assistance": 3
  },
  "user_terms": ["quick tidy", "stock check", "scan area", "bring stuff"],
  "last_updated": "2024-03-20T18:30:00Z"
}
```

### **After 50 Interactions**
```json
{
  "total_interactions": 50,
  "learned_zones": 5,
  "learned_shortcuts": 8,
  "frequent_missions": {
    "cargo_transfer": 18,
    "inspection": 15,
    "general_assistance": 12,
    "maintenance": 5
  },
  "user_terms": ["quick tidy", "stock check", "scan area", "bring stuff", "patrol", "cleanup", "deliver", "check on"],
  "last_updated": "2024-03-22T14:15:00Z"
}
```

## 🔧 **Integration Points**

### **Server Integration**
```python
# In server.py, replace existing mission brain:
from fleet_control.brain.contextual_integration import ContextualMissionBrain

_mission_brain = ContextualMissionBrain(_backend_services, use_contextual_ai=True)._brain
```

### **API Enhancement**
```python
@app.post("/api/mobile/missions/preview")
async def mobile_preview_mission(request: MissionRequest):
    result = _mission_brain.preview_mission(
        request_text=request.requestText,
        requested_by=request.requestedBy,
        context=request.context
    )
    
    # Include contextual insights
    if "contextual_insights" in result:
        result["ai_learning"] = result["contextual_insights"]
    
    return result
```

### **Feedback Loop**
```python
@app.post("/api/mobile/missions/{mission_id}/feedback")
async def mission_feedback(mission_id: str, feedback: MissionFeedback):
    # Learn from execution results
    _mission_brain.learn_from_mission(mission_id, feedback.dict())
    return {"success": True}
```

## 🎯 **Benefits Achieved**

### **Progressive Intelligence**
- **Starts with cottage knowledge** - Immediate contextual understanding
- **Learns user terminology** - Adapts to individual language patterns
- **Builds interaction patterns** - Improves with each mission
- **Remembers preferences** - Personalizes over time

### **Enhanced User Experience**
- **Natural language understanding** - Less clarification needed
- **Intelligent assumptions** - Fills missing context automatically
- **Personalized responses** - Tailored to user patterns
- **Progressive simplification** - Gets easier with use

### **Operational Efficiency**
- **Better mission planning** - More accurate task breakdown
- **Optimized robot selection** - Based on learned patterns
- **Reduced clarifications** - Faster mission execution
- **Improved success rates** - Learning from failures

## 🚀 **Future Enhancements**

### **Advanced Learning**
- **Temporal patterns** - Time-based preference learning
- **Multi-user adaptation** - Different learning per user
- **Environmental changes** - Adapting to cottage modifications
- **Seasonal patterns** - Weather and seasonal awareness

### **Integration Expansion**
- **IoT sensor data** - Environmental context from sensors
- **Voice adaptation** - Speech pattern learning
- **Visual learning** - Camera-based object recognition
- **Predictive assistance** - Anticipatory mission suggestions

The contextual AI system transforms the fleet management from a static rule-based system into a **learning, adaptive assistant** that truly understands your cottage environment and personal preferences.
