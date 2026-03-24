from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional
import uvicorn

app = FastAPI(title="Warehouse AI Engine", version="1.0.0")

# Pydantic models
class IntentRequest(BaseModel):
    request_id: str
    text: str
    context: Optional[Dict] = {}

class IntentResponse(BaseModel):
    request_id: str
    intent: str
    confidence: float
    entities: Dict
    timestamp: str

class MissionPlan(BaseModel):
    mission_id: str
    mission_type: str
    description: str
    priority: str
    estimated_duration: int

class AnalyticsRequest(BaseModel):
    query: str
    time_range: Optional[str] = "24h"

class OptimizationRequest(BaseModel):
    optimization_type: str
    parameters: Dict

# Health check
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ai-engine",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Warehouse AI Engine",
        "status": "running",
        "capabilities": [
            "intent-parsing",
            "mission-planning", 
            "knowledge-search",
            "analytics-prediction",
            "workflow-optimization"
        ]
    }

# Intent parsing endpoint
@app.post("/api/ai/intent-parse", response_model=IntentResponse)
async def intent_parse(request: IntentRequest):
    # Simple intent parsing logic
    text_lower = request.text.lower()
    
    if "pick" in text_lower or "retrieve" in text_lower:
        intent = "pick_items"
        confidence = 0.95
        entities = {
            "action": "pick",
            "quantity": 5,
            "location": "zone B"
        }
    elif "move" in text_lower or "transport" in text_lower:
        intent = "move_items"
        confidence = 0.88
        entities = {
            "action": "move",
            "from_location": "zone A",
            "to_location": "zone B"
        }
    else:
        intent = "unknown"
        confidence = 0.45
        entities = {}
    
    return IntentResponse(
        request_id=request.request_id,
        intent=intent,
        confidence=confidence,
        entities=entities,
        timestamp=datetime.utcnow().isoformat()
    )

# Mission planning endpoint
@app.post("/api/ai/mission-plan", response_model=MissionPlan)
async def plan_mission(request: dict):
    mission_id = f"mission-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    return MissionPlan(
        mission_id=mission_id,
        mission_type="picking",
        description="Pick items from zone B and deliver to shipping",
        priority="high",
        estimated_duration=45
    )

# Knowledge search endpoint
@app.post("/api/ai/knowledge-search")
async def knowledge_search(request: dict):
    return {
        "query": request.get("query", ""),
        "results": [
            {
                "content": "Standard picking procedure for zone B",
                "relevance": 0.92,
                "source": "warehouse_procedures"
            },
            {
                "content": "Robot navigation patterns for zone B",
                "relevance": 0.87,
                "source": "robot_manual"
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

# Analytics prediction endpoint
@app.post("/api/ai/analytics-predict")
async def analytics_predict(request: AnalyticsRequest):
    return {
        "query": request.query,
        "predictions": {
            "order_volume": "increase_15%",
            "robot_utilization": "78%",
            "completion_time": "2.3_hours"
        },
        "confidence": 0.84,
        "timestamp": datetime.utcnow().isoformat()
    }

# Optimization endpoint
@app.post("/api/ai/optimize")
async def optimize(request: OptimizationRequest):
    return {
        "optimization_type": request.optimization_type,
        "recommendations": [
            "Increase robot allocation to zone B by 2 units",
            "Adjust picking sequence to reduce travel time",
            "Optimize charging schedule during peak hours"
        ],
        "estimated_improvement": "23%",
        "timestamp": datetime.utcnow().isoformat()
    }

# Integration status endpoint
@app.get("/api/integration/status")
async def integration_status():
    return {
        "services": {
            "digital_twin_service": {
                "status": "connected",
                "url": "http://warehouse-digital-twin",
                "last_check": datetime.utcnow().isoformat()
            },
            "integration_hub": {
                "status": "connected", 
                "url": "http://warehouse-integration-hub",
                "last_check": datetime.utcnow().isoformat()
            }
        },
        "message_queues": {
            "service_bus": "connected",
            "queues": ["warehouse-digital-twin-service", "warehouse-ai-engine", "warehouse-integration-hub"]
        },
        "overall_status": "healthy"
    }

# DTDL Generator endpoints
@app.post("/api/dtdl/conversation")
async def dtdl_conversation(request: dict):
    """Start or continue DTDL model creation conversation with AI assistance"""
    from dtdl_generator import dtdl_generator
    from azure_openai_integration import azure_openai_generator
    
    conversation_id = request.get("conversation_id", f"conv-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    user_input = request.get("user_input", "")
    model_type = request.get("model_type", "warehouse")
    
    # Try Azure OpenAI first, fallback to pattern matching
    try:
        entities = await azure_openai_generator.extract_entities_with_ai(user_input, model_type)
        dtdl_model = await azure_openai_generator.generate_complete_dtdl_with_ai(user_input, model_type)
        suggestions = await azure_openai_generator.get_suggestions_with_ai(dtdl_model, model_type)
        
        ai_method = "azure_openai"
    except Exception as e:
        print(f"Azure OpenAI failed, using fallback: {e}")
        # Fallback to pattern matching
        entities = dtdl_generator.extract_entities_from_input(user_input, model_type)
        dtdl_model = dtdl_generator.generate_dtdl_model(conversation_id, model_type, entities)
        suggestions = dtdl_generator.suggest_improvements(dtdl_model, model_type)
        
        ai_method = "pattern_matching"
    
    # Validate model
    validation = dtdl_generator.validate_dtdl_model(dtdl_model)
    
    return {
        "conversation_id": conversation_id,
        "model_type": model_type,
        "user_input": user_input,
        "ai_method": ai_method,
        "extracted_entities": entities,
        "generated_dtdl": dtdl_model,
        "validation": validation,
        "suggestions": suggestions,
        "ai_status": {
            "azure_openai_available": await azure_openai_generator.is_available(),
            "method_used": ai_method
        },
        "next_steps": [
            "Review the generated DTDL model",
            "Add more properties or relationships if needed",
            "Validate and register the model",
            "Create twin instances"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/dtdl/generate")
async def generate_dtdl_model(request: dict):
    """Generate DTDL model from detailed specification"""
    from dtdl_generator import dtdl_generator
    
    model_type = request.get("model_type", "warehouse")
    properties = request.get("properties", [])
    relationships = request.get("relationships", [])
    telemetry = request.get("telemetry", [])
    
    entities = {
        "properties": properties,
        "relationships": relationships,
        "telemetry": telemetry
    }
    
    dtdl_model = dtdl_generator.generate_dtdl_model("manual", model_type, entities)
    validation = dtdl_generator.validate_dtdl_model(dtdl_model)
    
    return {
        "model_type": model_type,
        "dtdl_model": dtdl_model,
        "validation": validation,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/dtdl/validate")
async def validate_dtdl_model(request: dict):
    """Validate existing DTDL model"""
    from dtdl_generator import dtdl_generator
    
    dtdl_model = request.get("dtdl_model", {})
    validation = dtdl_generator.validate_dtdl_model(dtdl_model)
    
    return {
        "validation": validation,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/dtdl/templates")
async def get_dtdl_templates():
    """Get DTDL templates for different model types"""
    from dtdl_generator import dtdl_generator
    
    return {
        "templates": dtdl_generator.dtdl_templates,
        "available_model_types": list(dtdl_generator.dtdl_templates.keys()),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
