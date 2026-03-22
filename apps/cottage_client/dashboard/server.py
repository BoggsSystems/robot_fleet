import asyncio
import json
import subprocess
import time
from typing import Any, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from fleet_control import LocalRuntimeConfig, ShadowWorldStore
from fleet_control.brain import LocalMissionBrain
from fleet_control.services import FleetBackendServices

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory reference to the running FleetController
_fleet_controller = None
_backend_services = FleetBackendServices(store=ShadowWorldStore(), config=LocalRuntimeConfig())
_backend_services.ensure_defaults()
_mission_brain = LocalMissionBrain(_backend_services)

def set_fleet_controller(controller):
    global _fleet_controller
    _fleet_controller = controller

# Pydantic models for request validation
class RobotConnectionTest(BaseModel):
    ip: str
    interface: str = "lo0"

class RobotConfig(BaseModel):
    robotId: str
    name: str
    ipAddress: str
    networkInterface: str
    zone: str
    subZone: str
    capabilities: list
    model: str = "Unitree R1"
    serial: str = ""
    firmware: str = ""
    robotType: str = "unitree_r1"
    robotCategory: str = "Humanoid"
    vendor: str = "unitree_sdk2"

class CalibrationRequest(BaseModel):
    robotId: str
    step: str
    ip: str

class SimulationRequest(BaseModel):
    robotId: str
    scenario: str


class FleetCreateRequest(BaseModel):
    fleetId: str
    name: str
    status: str = "active"


class SiteCreateRequest(BaseModel):
    siteId: str
    name: str
    status: str = "active"


class ZoneCreateRequest(BaseModel):
    zoneId: str
    siteId: str
    name: str
    zoneType: str = "operational"
    parentZoneId: Optional[str] = None


class TaskCreateRequest(BaseModel):
    taskType: str
    spec: dict
    robotId: Optional[str] = None
    zoneId: Optional[str] = None


class TaskAssignRequest(BaseModel):
    robotId: str


class CommandCreateRequest(BaseModel):
    robotId: str
    commandType: str
    parameters: dict
    issuedBy: str = "operator@local"


class OnboardingUpdateRequest(BaseModel):
    stage: str
    status: str
    details: dict = {}


class MissionRequest(BaseModel):
    requestText: str
    requestedBy: str = "operator@local"
    context: dict = {}


class MissionClarificationRequest(BaseModel):
    answer: str


class MissionConfirmRequest(BaseModel):
    confirmedBy: str = "operator@local"


class MobileMissionQuestionResponse(BaseModel):
    mission_id: str
    prompt: str
    field_name: str
    reason: str


class MobileMissionResponse(BaseModel):
    missionId: str
    title: str
    requestText: str
    status: str
    missionType: str
    from_: Optional[str] = Field(default=None, alias="from")
    to: Optional[str] = None
    assignedRobotId: Optional[str] = None
    taskCount: int
    taskIds: list[str]
    clarificationRequired: bool
    clarificationQuestion: Optional[MobileMissionQuestionResponse] = None
    summary: str
    createdAt: str
    updatedAt: str

    model_config = {"populate_by_name": True}


class MissionPreviewPayloadResponse(BaseModel):
    status: str
    intent_provider: Optional[str] = None
    question: Optional[dict[str, Any]] = None
    intent: Optional[dict[str, Any]] = None
    resources: Optional[dict[str, Any]] = None
    plan: Optional[dict[str, Any]] = None
    explanation: Optional[dict[str, Any]] = None


class MobileMissionPreviewEnvelope(BaseModel):
    mission: MobileMissionResponse
    preview: MissionPreviewPayloadResponse


class MobileMissionDispatchEnvelope(BaseModel):
    mission: MobileMissionResponse
    dispatch: Optional[dict[str, Any]] = None


class MobileMissionListEnvelope(BaseModel):
    missions: list[MobileMissionResponse]


class MobileMissionDetailEnvelope(BaseModel):
    mission: MobileMissionResponse
    preview: MissionPreviewPayloadResponse


def _dispatch_preview_result(request_text: str, requested_by: str, context: dict, result: dict) -> dict:
    plan = result["plan"]
    created_tasks = []
    assignments_by_task = {
        assignment["task_id"]: assignment
        for assignment in plan.get("assignments", [])
    }

    for planned_task in plan.get("tasks", []):
        requirements = planned_task.get("requirements", {})
        task_record = _backend_services.create_task(
            task_type=planned_task["task_type"],
            spec={
                "mission_id": plan["mission_id"],
                "summary": planned_task["summary"],
                "source_zone": requirements.get("source_zone"),
                "destination_zone": requirements.get("destination_zone"),
                "required_capabilities": requirements.get("required_capabilities", []),
                "preferred_robot_types": requirements.get("preferred_robot_types", []),
                "minimum_battery_level": requirements.get("minimum_battery_level"),
                "payload_weight_kg": requirements.get("payload_weight_kg"),
                "estimated_duration_minutes": planned_task.get("estimated_duration_minutes"),
                "route": f"{requirements.get('source_zone') or 'site'} -> {requirements.get('destination_zone') or requirements.get('source_zone') or 'site'}",
                "type": planned_task["task_type"],
                "context": context,
            },
            zone_id=requirements.get("source_zone"),
        )
        assignment = assignments_by_task.get(planned_task["task_id"])
        if assignment:
            task_record = _backend_services.assign_task(task_record["task_id"], assignment["robot_id"])
        created_tasks.append(task_record)

    return {
        "status": result["status"],
        "mission": {
            "mission_id": plan["mission_id"],
            "mission_type": plan["mission_type"],
            "request_text": request_text,
            "requested_by": requested_by,
        },
        "plan": plan,
        "created_tasks": created_tasks,
        "explanation": result.get("explanation"),
    }


def _normalize_preview_mission_id(result: dict, mission_id: str) -> dict:
    if result.get("status") == "clarification_required":
        question = dict(result.get("question", {}))
        question["mission_id"] = mission_id
        normalized = dict(result)
        normalized["question"] = question
        return normalized

    normalized = dict(result)
    intent = dict(normalized.get("intent", {}))
    intent["mission_id"] = mission_id
    plan = dict(normalized.get("plan", {}))
    plan["mission_id"] = mission_id
    plan["tasks"] = [
        {**task, "mission_id": mission_id}
        for task in plan.get("tasks", [])
    ]
    plan["assignments"] = [
        {**assignment, "mission_id": mission_id}
        for assignment in plan.get("assignments", [])
    ]
    explanation = dict(normalized.get("explanation", {}))
    if explanation:
        explanation["mission_id"] = mission_id
    normalized["intent"] = intent
    normalized["plan"] = plan
    normalized["explanation"] = explanation
    return normalized


def _mobile_mission_view(session: dict) -> dict:
    preview = session.get("preview") or {}
    plan = preview.get("plan") or {}
    intent = preview.get("intent") or {}
    explanation = preview.get("explanation") or {}
    task_records = [
        _backend_services.store.get_task_record(task_id)
        for task_id in session.get("task_ids", [])
    ]
    task_records = [task for task in task_records if task is not None]

    if task_records:
        statuses = {task["status"] for task in task_records}
        if "failed" in statuses:
            current_status = "blocked"
        elif statuses <= {"completed"}:
            current_status = "completed"
        elif "assigned" in statuses or "running" in statuses or "queued" in statuses:
            current_status = "in_progress"
        else:
            current_status = session["status"]
    else:
        current_status = session["status"]

    assigned_robot = None
    if plan.get("assignments"):
        assigned_robot = plan["assignments"][0].get("robot_id")
    elif task_records and task_records[0].get("robot_id"):
        assigned_robot = task_records[0]["robot_id"]

    return {
        "missionId": session["mission_id"],
        "title": intent.get("objective") or session["request_text"],
        "requestText": session["request_text"],
        "status": current_status,
        "missionType": intent.get("mission_type") or plan.get("mission_type") or "general_assistance",
        "from_": intent.get("source_zone"),
        "to": intent.get("destination_zone"),
        "assignedRobotId": assigned_robot,
        "taskCount": len(plan.get("tasks", [])),
        "taskIds": session.get("task_ids", []),
        "clarificationRequired": session["status"] == "clarification_required",
        "clarificationQuestion": session.get("question") or None,
        "summary": explanation.get("summary") or preview.get("status") or session["status"],
        "createdAt": session["created_at"],
        "updatedAt": session["updated_at"],
    }


def _apply_clarification_to_text(session: dict, answer: str) -> str:
    question = session.get("question") or {}
    field_name = question.get("field_name")
    request_text = session["request_text"].rstrip(". ")
    answer = answer.strip()
    if field_name == "source_zone":
        return f"{request_text} from {answer}"
    if field_name == "destination_zone":
        return f"{request_text} to {answer}"
    return f"{request_text}. {answer}"

@app.get("/api/fleet/status")
async def get_fleet_status():
    if _fleet_controller is None:
        return {
            "robots": _backend_services.list_robots(),
            "active_tasks": [],
            "completed_tasks": [],
            "onboarding_mode": True,
            "registry": _backend_services.fleet_overview(),
        }
    status = _fleet_controller.get_fleet_status()
    status["registry"] = _backend_services.fleet_overview()
    status["onboarding_mode"] = False
    return status


@app.get("/api/brain/resources")
async def get_brain_resources():
    return _mission_brain.assess_resources()


@app.post("/api/brain/preview")
async def preview_mission(request: MissionRequest):
    return _mission_brain.preview_mission(
        request.requestText,
        requested_by=request.requestedBy,
        context=request.context,
    )


@app.post("/api/brain/dispatch")
async def dispatch_mission(request: MissionRequest):
    result = _mission_brain.preview_mission(
        request.requestText,
        requested_by=request.requestedBy,
        context=request.context,
    )
    if result["status"] == "clarification_required":
        return result
    return _dispatch_preview_result(request.requestText, request.requestedBy, request.context, result)


@app.post("/api/mobile/missions/preview", response_model=MobileMissionPreviewEnvelope)
async def mobile_preview_mission(request: MissionRequest):
    result = _mission_brain.preview_mission(
        request.requestText,
        requested_by=request.requestedBy,
        context=request.context,
    )
    mission_id = (
        result.get("question", {}).get("mission_id")
        if result["status"] == "clarification_required"
        else result["plan"]["mission_id"]
    )
    result = _normalize_preview_mission_id(result, mission_id)
    session = _backend_services.upsert_mission_session(
        mission_id=mission_id,
        request_text=request.requestText,
        requested_by=request.requestedBy,
        status=result["status"],
        preview=result,
        question=result.get("question", {}),
        metadata={"context": request.context, "intent_provider": result.get("intent_provider")},
    )
    return {"mission": _mobile_mission_view(session), "preview": result}


@app.post("/api/mobile/missions/{mission_id}/clarify", response_model=MobileMissionPreviewEnvelope)
async def mobile_clarify_mission(mission_id: str, request: MissionClarificationRequest):
    session = _backend_services.get_mission_session(mission_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    if session["status"] != "clarification_required":
        raise HTTPException(status_code=409, detail="Mission does not require clarification")

    updated_text = _apply_clarification_to_text(session, request.answer)
    context = dict(session.get("metadata", {}).get("context", {}))
    context["clarification_answer"] = request.answer
    result = _mission_brain.preview_mission(
        updated_text,
        requested_by=session["requested_by"],
        context=context,
    )
    result = _normalize_preview_mission_id(result, mission_id)
    updated = _backend_services.upsert_mission_session(
        mission_id=mission_id,
        request_text=updated_text,
        requested_by=session["requested_by"],
        status=result["status"],
        preview=result,
        question=result.get("question", {}),
        task_ids=session.get("task_ids", []),
        metadata={"context": context, "intent_provider": result.get("intent_provider")},
        created_at=session["created_at"],
    )
    return {"mission": _mobile_mission_view(updated), "preview": result}


@app.post("/api/mobile/missions/{mission_id}/confirm", response_model=MobileMissionDispatchEnvelope)
async def mobile_confirm_mission(mission_id: str, request: MissionConfirmRequest):
    session = _backend_services.get_mission_session(mission_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    if session["status"] == "clarification_required":
        raise HTTPException(status_code=409, detail="Mission still requires clarification")
    if session["status"] == "cancelled":
        raise HTTPException(status_code=409, detail="Mission has been cancelled")

    preview = session.get("preview") or {}
    if not preview or preview.get("status") not in {"ok", "blocked"}:
        raise HTTPException(status_code=409, detail="Mission preview is not ready for confirmation")
    if preview.get("status") == "blocked":
        updated = _backend_services.upsert_mission_session(
            mission_id=mission_id,
            request_text=session["request_text"],
            requested_by=session["requested_by"],
            status="blocked",
            preview=preview,
            question=session.get("question", {}),
            task_ids=session.get("task_ids", []),
            metadata={**session.get("metadata", {}), "confirmed_by": request.confirmedBy},
            created_at=session["created_at"],
        )
        return {"mission": _mobile_mission_view(updated), "dispatch": None}

    dispatch = _dispatch_preview_result(
        session["request_text"],
        session["requested_by"],
        session.get("metadata", {}).get("context", {}),
        preview,
    )
    updated = _backend_services.upsert_mission_session(
        mission_id=mission_id,
        request_text=session["request_text"],
        requested_by=session["requested_by"],
        status="dispatched",
        preview=preview,
        question={},
        task_ids=[task["task_id"] for task in dispatch["created_tasks"]],
        metadata={**session.get("metadata", {}), "confirmed_by": request.confirmedBy},
        created_at=session["created_at"],
    )
    return {"mission": _mobile_mission_view(updated), "dispatch": dispatch}


@app.get("/api/mobile/missions", response_model=MobileMissionListEnvelope)
async def mobile_list_missions():
    sessions = _backend_services.list_mission_sessions()
    return {"missions": [_mobile_mission_view(session) for session in sessions]}


@app.get("/api/mobile/missions/{mission_id}", response_model=MobileMissionDetailEnvelope)
async def mobile_get_mission(mission_id: str):
    session = _backend_services.get_mission_session(mission_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    return {"mission": _mobile_mission_view(session), "preview": session.get("preview", {})}


@app.post("/api/mobile/missions/{mission_id}/cancel", response_model=MobileMissionDispatchEnvelope)
async def mobile_cancel_mission(mission_id: str):
    session = _backend_services.get_mission_session(mission_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    updated = _backend_services.upsert_mission_session(
        mission_id=mission_id,
        request_text=session["request_text"],
        requested_by=session["requested_by"],
        status="cancelled",
        preview=session.get("preview", {}),
        question=session.get("question", {}),
        task_ids=session.get("task_ids", []),
        metadata=session.get("metadata", {}),
        created_at=session["created_at"],
    )
    return {"mission": _mobile_mission_view(updated), "dispatch": None}

@app.post("/api/robots/test-connection")
async def test_connection(request: RobotConnectionTest):
    """Test connection to a robot at the given IP."""
    try:
        # Simulate connection test with the robot
        # In production, this would actually ping the robot and check DDS connection
        time.sleep(0.5)  # Simulate network delay
        
        # Mock successful connection - in production, this would:
        # 1. Ping the robot IP
        # 2. Initialize DDS channel
        # 3. Query robot info via SDK
        return {
            "success": True,
            "model": "Unitree R1",
            "serial": f"R1-2024-{hash(request.ip) % 10000:04d}",
            "firmware": "v2.1.4",
            "battery": 87,
            "message": "Connection successful"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@app.post("/api/robots/register")
async def register_robot(config: RobotConfig):
    """Register a new robot to the fleet."""
    try:
        site_id = config.zone or LocalRuntimeConfig().site_id
        zone_id = config.subZone or config.zone
        robot_record = _backend_services.register_robot(
            robot_id=config.robotId,
            name=config.name,
            ip_address=config.ipAddress,
            network_interface=config.networkInterface,
            capabilities=list(config.capabilities),
            site_id=site_id,
            zone_id=zone_id,
            model=config.model,
            serial=config.serial,
            firmware=config.firmware,
            robot_type=config.robotType,
            robot_category=config.robotCategory,
            vendor=config.vendor,
            metadata={"zone_label": config.zone, "sub_zone_label": config.subZone},
        )
        
        # If fleet controller exists, register with it
        if _fleet_controller:
            from fleet_control.robot_manager import RobotManager
            manager = RobotManager(
                robot_id=config.robotId,
                host=config.ipAddress,
                sim=False,
                domain_id=0,
                interface=config.networkInterface,
                robot_type=config.robotType,
                vendor=config.vendor
            )
            _fleet_controller.register_robot(config.robotId, manager)
        
        return {
            "success": True,
            "message": f"Robot {config.name} ({config.robotType}) registered successfully",
            "robot": robot_record,
            "onboarding": _backend_services.get_onboarding(config.robotId),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/robots/calibrate")
async def calibrate_robot(request: CalibrationRequest):
    """Run calibration step for a robot."""
    try:
        # Simulate calibration process
        # In production, this would send actual SDK commands
        step_messages = {
            "diagnostics": "All systems nominal - CPU: 45°C, Motors: OK, Battery: Healthy",
            "stand": "Robot standing successfully - Balance check passed",
            "movement": "Movement test complete - Forward 1m, Turn 90°, Return"
        }
        
        # Simulate processing time
        time.sleep(1.0)
        
        if request.step in step_messages:
            onboarding = _backend_services.record_calibration_step(
                request.robotId,
                request.step,
                True,
                step_messages[request.step],
            )
            return {
                "success": True,
                "step": request.step,
                "message": step_messages[request.step],
                "onboarding": onboarding,
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown calibration step: {request.step}")
            
    except HTTPException:
        raise
    except Exception as e:
        try:
            _backend_services.record_calibration_step(request.robotId, request.step, False, str(e))
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Calibration failed: {str(e)}")

@app.post("/api/robots/simulate")
async def run_simulation(request: SimulationRequest):
    """Run MuJoCo simulation for a robot."""
    try:
        scenario_messages = {
            "basic": "Basic navigation completed successfully - 2m walk, 90° turn executed",
            "warehouse": "Warehouse simulation completed - 5 obstacles avoided, path optimized",
            "emergency": "Emergency stop test passed - Robot stopped within 0.3s of signal",
            "battery": "Battery simulation completed - Low-battery behavior verified"
        }
        
        # Simulate processing time based on scenario
        delay = {"basic": 1, "warehouse": 2, "emergency": 1.5, "battery": 3}
        time.sleep(delay.get(request.scenario, 1))
        
        return {
            "success": True,
            "scenario": request.scenario,
            "message": scenario_messages.get(request.scenario, "Simulation completed"),
            "metrics": {
                "duration": delay.get(request.scenario, 1),
                "success_rate": 0.95
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@app.get("/api/backend/overview")
async def get_backend_overview():
    return _backend_services.fleet_overview()


@app.get("/api/backend/fleets")
async def list_fleets():
    return {"fleets": _backend_services.list_fleets()}


@app.post("/api/backend/fleets")
async def create_fleet(request: FleetCreateRequest):
    return {"fleet": _backend_services.create_fleet(request.fleetId, request.name, request.status)}


@app.get("/api/backend/sites")
async def list_sites():
    return {"sites": _backend_services.list_sites()}


@app.post("/api/backend/sites")
async def create_site(request: SiteCreateRequest):
    return {"site": _backend_services.create_site(request.siteId, request.name, request.status)}


@app.get("/api/backend/zones")
async def list_zones(site_id: str | None = None):
    return {"zones": _backend_services.list_zones(site_id=site_id)}


@app.post("/api/backend/zones")
async def create_zone(request: ZoneCreateRequest):
    return {
        "zone": _backend_services.create_zone(
            request.zoneId,
            request.siteId,
            request.name,
            request.zoneType,
            request.parentZoneId,
        )
    }


@app.get("/api/backend/robots")
async def list_robots():
    return {"robots": _backend_services.list_robots()}


@app.get("/api/backend/robots/{robot_id}/onboarding")
async def get_robot_onboarding(robot_id: str):
    onboarding = _backend_services.get_onboarding(robot_id)
    if onboarding is None:
        raise HTTPException(status_code=404, detail=f"Robot {robot_id} not found")
    return {"onboarding": onboarding}


@app.post("/api/backend/robots/{robot_id}/onboarding")
async def update_robot_onboarding(robot_id: str, request: OnboardingUpdateRequest):
    try:
        return {
            "onboarding": _backend_services.update_onboarding(
                robot_id,
                stage=request.stage,
                status=request.status,
                details=request.details,
            )
        }
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/api/backend/tasks")
async def list_tasks(status: str | None = None):
    return {"tasks": _backend_services.list_tasks(status=status)}


@app.post("/api/backend/tasks")
async def create_task(request: TaskCreateRequest):
    task = _backend_services.create_task(
            task_type=request.taskType,
            spec=request.spec,
            robot_id=request.robotId,
            zone_id=request.zoneId,
        )
    if request.robotId:
        task = _backend_services.assign_task(task["task_id"], request.robotId)
    return {"task": task}


@app.post("/api/backend/tasks/{task_id}/assign")
async def assign_task(task_id: str, request: TaskAssignRequest):
    try:
        return {"task": _backend_services.assign_task(task_id, request.robotId)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/api/backend/tasks/{task_id}/execute")
async def execute_task(task_id: str):
    try:
        return {"task": _backend_services.execute_task(task_id, controller=_fleet_controller)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/api/backend/commands")
async def list_commands(robot_id: str | None = None):
    return {"commands": _backend_services.list_commands(robot_id=robot_id)}


@app.post("/api/backend/commands")
async def create_command(request: CommandCreateRequest):
    return {
        "command": _backend_services.create_command(
            robot_id=request.robotId,
            command_type=request.commandType,
            parameters=request.parameters,
            issued_by=request.issuedBy,
        )
    }


@app.post("/api/backend/commands/{command_id}/dispatch")
async def dispatch_command(command_id: str):
    try:
        return {"command": _backend_services.dispatch_command(command_id, controller=_fleet_controller)}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if _fleet_controller is not None:
                status = _fleet_controller.get_fleet_status()
                status["registry"] = _backend_services.fleet_overview()
                status["onboarding_mode"] = False
            else:
                # Return onboarding mode status with registered robots
                status = {
                    "robots": _backend_services.list_robots(),
                    "active_tasks": [],
                    "completed_tasks": [],
                    "onboarding_mode": True,
                    "registry": _backend_services.fleet_overview(),
                }
            # Broadcast the live position and task metrics
            await websocket.send_text(json.dumps(status))
            # Stream at 20Hz (every 50ms)
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        print("Dashboard client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket error: {e}")

def run_server(controller, port=8000):
    global _fleet_controller
    _fleet_controller = controller
    import uvicorn
    # Important: Run programmatically since we share the controller memory
    print(f"Starting dashboard telemetry server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
