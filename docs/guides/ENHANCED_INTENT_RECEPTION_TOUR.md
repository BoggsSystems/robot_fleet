# 🧠 Updated Tour: Intent Reception at Backend

## 📥 **Intent Reception Entry Points**

### **1. API Endpoints for Intent Reception**

#### **Primary Mission Preview Endpoint**
```python
@app.post("/api/mobile/missions/preview", response_model=MobileMissionPreviewEnvelope)
async def mobile_preview_mission(request: MissionRequest):
    """
    Primary entry point for user intent processing.
    Receives natural language request and returns mission preview.
    """
    result = _mission_brain.preview_mission(
        request.requestText,           # "Scan kitchen for QR codes"
        requested_by=request.requestedBy,  # "user@ios_app"
        context=request.context,       # Optional context dict
    )
    
    # Process and return result
    mission_id = extract_mission_id(result)
    session = create_mission_session(mission_id, request, result)
    
    return MobileMissionPreviewEnvelope(
        mission=_mobile_mission_view(session),
        preview=result
    )
```

#### **Mission Request Model**
```python
class MissionRequest(BaseModel):
    requestText: str              # User natural language input
    requestedBy: str              # User identifier
    context: Optional[dict] = None  # Additional context (location, time, etc.)

# Example request:
{
    "requestText": "Scan the kitchen area for QR codes and report findings",
    "requestedBy": "user@ios_app",
    "context": {
        "currentLocation": "living_room",
        "timeOfDay": "morning",
        "urgency": "normal"
    }
}
```

### **2. Mission Brain Processing**

#### **Enhanced Mission Brain with RAG Integration**
```python
class ContextualMissionBrain:
    """Enhanced mission brain with RAG integration"""
    
    def __init__(self, services: FleetBackendServices, use_contextual_ai: bool = True):
        self.services = services
        self.use_contextual_ai = use_contextual_ai
        
        if use_contextual_ai:
            # Initialize RAG-enhanced intent service
            self.intent_service = ContextualIntentService()
            self.rag_system = MultiTenantRAG()
        else:
            # Fallback to original intent service
            self.intent_service = OpenAIIntentService()
    
    def preview_mission(self, request_text: str, requested_by: str, context: dict = None) -> dict:
        """
        Process user intent and generate mission preview with RAG enhancement.
        """
        # 1. Get current resource snapshot
        resources = self.assess_resources()
        
        # 2. Parse intent with enhanced context
        if self.use_contextual_ai:
            parsed_intent = self.intent_service.parse_request(
                request_text=request_text,
                requested_by=requested_by,
                context=context
            )
        else:
            parsed_intent = self._fallback_intent_parsing(request_text, requested_by)
        
        # 3. Handle clarification needs
        if isinstance(parsed_intent, ClarificationQuestion):
            return {
                "status": "clarification_required",
                "question": parsed_intent.dict(),
                "mission_id": str(uuid4())
            }
        
        # 4. Generate mission plan with contextual knowledge
        proposal = self._build_proposal(parsed_intent, resources)
        
        return {
            "status": "ready",
            "plan": proposal,
            "contextual_insights": self._get_contextual_insights(parsed_intent, context)
        }
```

## 🔄 **Complete Intent Processing Flow**

### **Step 1: Request Reception**
```
iOS App → POST /api/mobile/missions/preview
{
    "requestText": "Scan kitchen for QR codes",
    "requestedBy": "user@ios_app",
    "context": {"currentLocation": "living_room"}
}
```

### **Step 2: Resource Assessment**
```python
def assess_resources(self) -> ResourceSnapshot:
    """
    Get current fleet resources and capabilities.
    """
    # Get all robots
    robots = self.services.list_robots()
    
    # Filter available robots
    available_robots = [
        robot for robot in robots 
        if robot["status"] == "available"
    ]
    
    # Get site graph for navigation
    site_graph = self.services.get_site_graph()
    
    return ResourceSnapshot(
        robots=available_robots,
        zones=site_graph.zones,
        constraints=self._get_current_constraints()
    )
```

### **Step 3: Enhanced Intent Parsing**
```python
class ContextualIntentService:
    """RAG-enhanced intent parsing service"""
    
    def parse_request(self, request_text: str, requested_by: str, context: dict = None) -> MissionIntent:
        """
        Parse user request with contextual knowledge from RAG system.
        """
        # 1. Get client context (e.g., "cot_12345678")
        client_id = self._get_client_id(requested_by)
        
        # 2. Search RAG for relevant knowledge
        rag_results = self.rag_system.search(client_id, request_text, limit=5)
        
        # 3. Build enhanced prompt with context
        enhanced_prompt = self._build_enhanced_prompt(
            query=request_text,
            rag_context=rag_results,
            user_context=context,
            client_id=client_id
        )
        
        # 4. Parse with OpenAI/LLM
        parsed_intent = self._parse_with_llm(enhanced_prompt, request_text)
        
        # 5. Learn from interaction
        self._learn_from_interaction(request_text, parsed_intent, rag_results, client_id)
        
        return parsed_intent
    
    def _build_enhanced_prompt(self, query: str, rag_context: list, user_context: dict, client_id: str) -> str:
        """
        Build enhanced prompt with RAG knowledge and user context.
        """
        # Extract relevant knowledge from RAG results
        cottage_knowledge = [r for r in rag_context if r["metadata"]["type"] == "zone"]
        robot_capabilities = [r for r in rag_context if r["metadata"]["type"] == "robot"]
        mission_templates = [r for r in rag_context if r["metadata"]["type"] == "mission"]
        
        prompt = f"""
COTTAGE CONTEXT:
You are operating in a residential cottage environment with the following knowledge:

ZONES:
{json.dumps([r["content"] for r in cottage_knowledge], indent=2)}

ROBOT CAPABILITIES:
{json.dumps([r["content"] for r in robot_capabilities], indent=2)}

MISSION TEMPLATES:
{json.dumps([r["content"] for r in mission_templates], indent=2)}

USER CONTEXT:
{json.dumps(user_context or {}, indent=2)}

USER REQUEST: {query}

Using this contextual knowledge, parse the user's intent into a structured mission plan.
Consider:
1. Which specific zone is involved based on cottage layout
2. Which robot is best suited based on capabilities
3. What procedures apply based on mission templates
4. Any cottage-specific constraints or preferences

Return a structured mission intent with:
- mission_type (inspection, transport, cleaning, assistance)
- objective (clear description of goal)
- source_zone and destination_zone
- required_capabilities
- priority
- constraints
"""
        return prompt
```

### **Step 4: Mission Proposal Generation**
```python
def _build_proposal(self, intent: MissionIntent, resources: ResourceSnapshot) -> dict:
    """
    Generate mission proposal with AI-powered task creation and robot assignment.
    """
    # 1. Get site graph for navigation
    site_graph = self.services.get_site_graph()
    
    # 2. Build tasks from intent using AI
    tasks = self._build_tasks(intent)  # AI-powered task generation
    
    # 3. Generate candidate steps with robot scoring
    candidate_steps = []
    for task in tasks:
        step = self._proposal_step(task, resources, site_graph)
        candidate_steps.append(step)
    
    # 4. Build rationale, assumptions, and operator notes
    rationale = self._build_rationale(candidate_steps)
    assumptions = self._proposal_assumptions(intent, resources)
    operator_notes = self._proposal_operator_notes(intent, resources)
    
    # 5. Add warnings if needed
    warnings = []
    if not resources.available_robot_ids:
        warnings.append("No robots are allocatable right now.")
    
    return {
        "mission_id": str(uuid4()),
        "candidate_steps": candidate_steps,
        "rationale": rationale,
        "assumptions": assumptions,
        "operator_notes": operator_notes,
        "warnings": warnings,
        "estimated_duration": self._estimate_duration(candidate_steps),
        "confidence_score": self._calculate_confidence(candidate_steps, resources)
    }
```

### **Step 5: AI-Powered Task Generation**
```python
def _build_tasks(self, intent: MissionIntent) -> list[PlannedTask]:
    """
    Use AI to generate appropriate tasks based on parsed intent.
    """
    if intent.mission_type == "inspection":
        return self._build_inspection_tasks(intent)
    elif intent.mission_type == "transport":
        return self._build_transport_tasks(intent)
    elif intent.mission_type == "cleaning":
        return self._build_cleaning_tasks(intent)
    elif intent.mission_type == "assistance":
        return self._build_assistance_tasks(intent)
    else:
        return self._build_general_tasks(intent)

def _build_inspection_tasks(self, intent: MissionIntent) -> list[PlannedTask]:
    """Generate inspection-specific tasks."""
    tasks = []
    
    # Main inspection task
    inspection_task = PlannedTask(
        task_id=str(uuid4()),
        task_type="inspection",
        requirements=TaskRequirements(
            source_zone=intent.source_zone,
            destination_zone=intent.source_zone,  # Same zone for inspection
            capabilities=["inspection", "qr_scanning"],
            duration_minutes=15,
            payload_requirements={}
        )
    )
    tasks.append(inspection_task)
    
    # Add reporting task if needed
    if "report" in intent.objective.lower():
        reporting_task = PlannedTask(
            task_id=str(uuid4()),
            task_type="reporting",
            requirements=TaskRequirements(
                source_zone=intent.source_zone,
                destination_zone="hub",  # Return to hub for reporting
                capabilities=["data_transfer", "reporting"],
                duration_minutes=5,
                payload_requirements={}
            )
        )
        tasks.append(reporting_task)
    
    return tasks
```

### **Step 6: Robot Assignment and Scoring**
```python
def _proposal_step(self, task: PlannedTask, resources: ResourceSnapshot, site_graph) -> dict:
    """
    Generate candidate robot assignments with scoring and rationale.
    """
    # 1. Filter available robots matching task requirements
    candidates = [
        robot for robot in resources.robots
        if robot["robot_id"] in resources.available_robot_ids 
        and self._matches_task(robot, task)
    ]
    
    # 2. Score candidates based on multiple factors
    scored_candidates = []
    for robot in candidates:
        score = self._score_candidate(robot, task)
        rationale = self._build_rationale(robot, task)
        
        scored_candidates.append({
            "robot_id": robot["robot_id"],
            "robot_name": robot["name"],
            "robot_type": robot["robot_type"],
            "score": round(score, 3),
            "rationale": rationale,
            "estimated_completion_time": self._estimate_task_time(robot, task)
        })
    
    # 3. Sort by score (highest first)
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "task_id": task.task_id,
        "task_type": task.task_type,
        "requirements": task.requirements.dict(),
        "candidate_allocations": scored_candidates[:3],  # Top 3 candidates
        "recommended_robot": scored_candidates[0] if scored_candidates else None
    }

def _score_candidate(self, robot: dict, task: PlannedTask) -> float:
    """
    Score robot suitability for task based on multiple factors.
    """
    score = 0.0
    
    # 1. Capability matching (40% weight)
    robot_caps = set(robot.get("capabilities", []))
    required_caps = set(task.requirements.capabilities)
    capability_match = len(robot_caps & required_caps) / len(required_caps)
    score += capability_match * 0.4
    
    # 2. Location proximity (25% weight)
    if robot.get("zone_id") == task.requirements.source_zone:
        score += 0.25
    elif self._is_adjacent_zone(robot.get("zone_id"), task.requirements.source_zone):
        score += 0.15
    
    # 3. Battery level (20% weight)
    battery = robot.get("metadata", {}).get("battery_level", 100)
    battery_score = battery / 100.0
    score += battery_score * 0.2
    
    # 4. Robot type preference (15% weight)
    type_preference = self._get_type_preference(task.task_type, robot["robot_type"])
    score += type_preference * 0.15
    
    return min(score, 1.0)  # Cap at 1.0
```

### **Step 7: Response Generation**
```python
# Final response structure
{
    "status": "ready",
    "plan": {
        "mission_id": "mission_12345678",
        "candidate_steps": [
            {
                "task_id": "task_12345678",
                "task_type": "inspection",
                "requirements": {
                    "source_zone": "kitchen",
                    "destination_zone": "kitchen",
                    "capabilities": ["inspection", "qr_scanning"],
                    "duration_minutes": 15
                },
                "candidate_allocations": [
                    {
                        "robot_id": "robot_quad_001",
                        "robot_name": "Quadruped 1",
                        "robot_type": "quadruped",
                        "score": 0.92,
                        "rationale": "Quadruped 1 is available in living_room, adjacent to kitchen, with 85% battery, and has inspection and qr_scanning capabilities.",
                        "estimated_completion_time": "15 minutes"
                    }
                ],
                "recommended_robot": {
                    "robot_id": "robot_quad_001",
                    "robot_name": "Quadruped 1"
                }
            }
        ],
        "rationale": "Mission involves scanning kitchen for QR codes. Quadruped robot recommended for indoor inspection with QR scanning capability.",
        "assumptions": [
            "Kitchen zone is accessible for robot navigation",
            "QR codes are within camera detection range",
            "Lighting conditions are adequate for scanning"
        ],
        "operator_notes": [
            "Ensure robot camera is calibrated before scanning",
            "Check for obstacles in kitchen navigation path",
            "Verify QR code readability conditions"
        ],
        "warnings": [],
        "estimated_duration": "15 minutes",
        "confidence_score": 0.87
    },
    "contextual_insights": {
        "zone_knowledge": "Kitchen has refrigerator, stove, sink, dishwasher landmarks",
        "robot_adaptation": "Quadruped preferred for indoor inspection tasks",
        "mission_template": "Standard inspection procedure with QR code scanning",
        "user_patterns": "User frequently requests kitchen area inspections"
    }
}
```

## 🔄 **Enhanced Features with RAG**

### **1. Contextual Understanding**
```python
# Traditional parsing vs RAG-enhanced parsing

# Traditional:
"Scan kitchen" → Basic inspection intent

# RAG-enhanced:
"Scan kitchen" → 
- Knows kitchen layout (refrigerator, stove, sink)
- Understands optimal scanning routes
- Recommends quadruped for indoor inspection
- Considers lighting conditions
- Applies learned user preferences
```

### **2. Learning and Adaptation**
```python
def _learn_from_interaction(self, request: str, intent: MissionIntent, rag_results: list, client_id: str):
    """
    Learn from user interaction to improve future responses.
    """
    # Record interaction
    interaction = {
        "request": request,
        "intent": intent.dict(),
        "rag_results": rag_results,
        "timestamp": datetime.now().isoformat(),
        "client_id": client_id
    }
    
    # Update user patterns
    self._update_user_patterns(interaction)
    
    # Improve RAG effectiveness
    self._update_rag_effectiveness(rag_results, intent)
    
    # Store for future learning
    self._store_interaction(interaction)
```

### **3. Multi-Client Support**
```python
# Different clients get different contextual knowledge

# Cottage client ("cot_12345678"):
"Scan kitchen" → Kitchen zone with residential layout, humanoid for detailed work

# Office client ("com_12345678"):
"Scan kitchen" → Break room/kitchenette with commercial layout, quadruped for patrol

# Hospital client ("hea_12345678"):
"Scan kitchen" -> Food service area with healthcare protocols, specialized robot
```

## 🎯 **Key Improvements**

### **Enhanced Accuracy**
- **Context-Aware**: Understands specific environment layouts
- **Robot Matching**: Better robot selection based on environment
- **Procedure Knowledge**: Uses appropriate procedures for context
- **User Adaptation**: Learns user preferences and terminology

### **Richer Responses**
- **Detailed Rationale**: Explains why specific robots and procedures are chosen
- **Contextual Insights**: Shows what knowledge was used
- **Assumptions & Notes**: Provides operational guidance
- **Confidence Scoring**: Indicates reliability of recommendations

### **Scalable Intelligence**
- **Multi-Environment**: Supports different environment types
- **Progressive Learning**: Improves with each interaction
- **Resource Optimization**: Better resource utilization
- **Error Reduction**: Fewer clarification requests needed

The enhanced intent reception system combines **RAG contextual knowledge** with **AI-powered reasoning** to provide sophisticated, environment-aware mission planning that learns and adapts over time!
