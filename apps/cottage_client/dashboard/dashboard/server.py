import asyncio
import json
import subprocess
import time
from typing import Any, Optional
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from fleet_control import LocalRuntimeConfig, ShadowWorldStore
from fleet_control.brain import LocalMissionBrain
from fleet_control.services import FleetBackendServices
from fleet_control.dynamic_pilot import list_available_tasks, estimate_task_execution
from .models import (
    # Request models
    RobotConnectionTest,
    RobotConfig,
    CalibrationRequest,
    SimulationRequest,
    FleetCreateRequest,
    SiteCreateRequest,
    ZoneCreateRequest,
    TaskCreateRequest,
    TaskAssignRequest,
    CommandCreateRequest,
    OnboardingUpdateRequest,
    MissionRequest,
    MissionClarificationRequest,
    MissionConfirmRequest,
    MissionControlRequest,
    TaskStatusUpdateRequest,
    MissionApprovalRequest,
    # Mobile models
    MobileMissionQuestionResponse,
    MissionEventResponse,
    MobileMissionResponse,
    MissionPreviewPayloadResponse,
    MobileMissionPreviewEnvelope,
    MobileMissionDispatchEnvelope,
    MobileMissionListEnvelope,
    MobileMissionDetailEnvelope,
)

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


def _dispatch_preview_result(request_text: str, requested_by: str, context: dict, result: dict) -> dict:
    plan = result["plan"]
    created_tasks = []
    planned_to_created: dict[str, str] = {}
    assignments_by_task = {
        assignment["task_id"]: assignment
        for assignment in plan.get("assignments", [])
    }

    for planned_task in plan.get("tasks", []):
        requirements = planned_task.get("requirements", {})
        assignment = assignments_by_task.get(planned_task["task_id"])
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
                "depends_on": planned_task.get("depends_on", []),
                "step_index": planned_task.get("metadata", {}).get("step_index"),
                "total_steps": len(plan.get("tasks", [])),
                "assignment_group": planned_task.get("metadata", {}).get("assignment_group"),
                "target_zone": planned_task.get("target_zone"),
                "planned_robot_id": assignment.get("robot_id") if assignment else None,
                "fallback_robot_ids": assignment.get("fallback_robot_ids", []) if assignment else [],
                "assignment_rationale": assignment.get("rationale") if assignment else None,
                "assignment_score": assignment.get("score") if assignment else None,
                "context": context,
            },
            zone_id=requirements.get("source_zone"),
        )
        planned_to_created[planned_task["task_id"]] = task_record["task_id"]
        task_record["spec"]["planned_task_id"] = planned_task["task_id"]
        if assignment and not planned_task.get("depends_on"):
            task_record = _backend_services.assign_task(task_record["task_id"], assignment["robot_id"])
        created_tasks.append(task_record)

    remapped_tasks = []
    for task_record in created_tasks:
        current = _backend_services.store.get_task_record(task_record["task_id"]) or task_record
        spec = dict(current.get("spec") or {})
        spec["planned_task_id"] = task_record.get("spec", {}).get("planned_task_id")
        depends_on = [
            planned_to_created.get(dependency, dependency)
            for dependency in spec.get("depends_on", [])
        ]
        spec["depends_on"] = depends_on
        current["spec"] = spec
        _backend_services.store.upsert_task_record(current)
        remapped_tasks.append(current)
    created_tasks = remapped_tasks

    activated_tasks = _backend_services.activate_ready_tasks()

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
        "activated_tasks": activated_tasks,
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


def _proposal_warnings(result: dict) -> list[str]:
    plan = dict(result.get("plan", {}))
    warnings = []
    for violation in plan.get("policy_violations", []) or []:
        if violation.get("severity") in {"warn", "error"}:
            warnings.append(str(violation.get("message") or violation.get("code") or "Policy warning"))
    return warnings


def _build_mission_request_record(mission_id: str, request_text: str, requested_by: str, context: dict, *, submitted_at: str, status: str) -> dict:
    return {
        "missionId": mission_id,
        "requestText": request_text,
        "requestedBy": requested_by,
        "context": context,
        "submittedAt": submitted_at,
        "status": status,
    }


def _build_mission_proposal_record(mission_id: str, result: dict, *, generated_at: str) -> dict:
    proposal = dict(result.get("proposal", {}))
    if proposal:
        proposal.setdefault("missionId", mission_id)
        proposal.setdefault("generatedAt", proposal.get("generated_at") or generated_at)
        proposal.setdefault("provider", result.get("intent_provider"))
        proposal.setdefault("warnings", [])
        proposal.setdefault("assumptions", [])
        return {
            "missionId": proposal.get("missionId", mission_id),
            "status": proposal.get("status", result.get("status", "unknown")),
            "provider": proposal.get("provider"),
            "question": result.get("question"),
            "intent": result.get("intent"),
            "resources": result.get("resources"),
            "plan": {
                "summary": proposal.get("plan_summary"),
                "candidate_steps": proposal.get("candidate_steps", []),
                "operator_notes": proposal.get("operator_notes", []),
            },
            "explanation": result.get("explanation"),
            "warnings": proposal.get("warnings", []),
            "assumptions": proposal.get("assumptions", []),
            "generatedAt": proposal.get("generatedAt"),
        }
    return {
        "missionId": mission_id,
        "status": result.get("status", "unknown"),
        "provider": result.get("intent_provider"),
        "question": result.get("question"),
        "intent": result.get("intent"),
        "resources": result.get("resources"),
        "plan": result.get("plan"),
        "explanation": result.get("explanation"),
        "warnings": _proposal_warnings(result),
        "assumptions": [],
        "generatedAt": generated_at,
    }


def _build_validated_plan_record(mission_id: str, result: dict, *, validated_at: str) -> dict:
    plan = dict(result.get("validated_plan") or result.get("plan", {}))
    policy_violations = list(plan.get("policy_violations", []) or [])
    blocking_reasons = list(plan.get("blocking_reasons", []) or [
        str(violation.get("message") or violation.get("code") or "Blocked")
        for violation in policy_violations
        if violation.get("severity") == "error"
    ])
    warnings = list(plan.get("warnings", []) or [
        str(violation.get("message") or violation.get("code") or "Warning")
        for violation in policy_violations
        if violation.get("severity") == "warn"
    ])
    return {
        "missionId": mission_id,
        "status": result.get("status", "unknown"),
        "executable": result.get("status") == "ok",
        "missionType": plan.get("mission_type") or dict(result.get("intent", {})).get("mission_type"),
        "tasks": plan.get("tasks", []),
        "assignments": plan.get("assignments", []),
        "policyViolations": policy_violations,
        "warnings": warnings,
        "blockingReasons": blocking_reasons,
        "explanation": plan.get("explanation") or dict(result.get("explanation", {})).get("summary"),
        "validatedAt": validated_at,
    }


def _pending_approval_record(mission_id: str, *, required: bool) -> dict:
    return {
        "missionId": mission_id,
        "required": required,
        "status": "pending" if required else "not_required",
        "decision": None,
        "approvedBy": None,
        "approvedAt": None,
        "notes": None,
    }


def _mobile_mission_view(session: dict) -> dict:
    preview = session.get("preview") or {}
    plan = preview.get("plan") or {}
    intent = preview.get("intent") or {}
    explanation = preview.get("explanation") or {}
    approval = session.get("approval") or {}
    replan = session.get("metadata", {}).get("pending_replan") or {}
    task_records = [
        _backend_services.store.get_task_record(task_id)
        for task_id in session.get("task_ids", [])
    ]
    task_records = [task for task in task_records if task is not None]
    task_records_by_id = {task["task_id"]: task for task in task_records}
    plan_tasks = sorted(plan.get("tasks", []), key=lambda task: task.get("metadata", {}).get("step_index", 999))

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

    completed_steps = sum(1 for task in task_records if task.get("status") == "completed")
    focused_task_record = next((task for task in task_records if task.get("status") == "failed"), None)
    active_plan_task = None
    for task in plan_tasks:
        if active_plan_task is not None or focused_task_record is not None:
            break
        task_record = task_records_by_id.get(task.get("task_id"))
        if task_record and task_record.get("status") in {"assigned", "running"}:
            focused_task_record = task_record
            active_plan_task = task
            break
        if task_record is None or task_record.get("status") != "completed":
            active_plan_task = task
            break
    if focused_task_record is None and task_records:
        focused_task_record = next(
            (
                task
                for task in task_records
                if task.get("status") in {"assigned", "running", "queued"}
            ),
            None,
        ) or task_records[-1]
    if active_plan_task is None and focused_task_record is not None:
        planned_task_id = dict(focused_task_record.get("spec") or {}).get("planned_task_id")
        active_plan_task = next(
            (
                task
                for task in plan_tasks
                if task.get("task_id") == planned_task_id
            ),
            None,
        )
    if active_plan_task is None and plan_tasks:
        active_plan_task = plan_tasks[-1]
    active_task_record = focused_task_record
    active_task_spec = dict(active_task_record.get("spec") or {}) if active_task_record else {}
    fallback_robot_ids = []
    if active_task_record:
        try:
            fallback_robot_ids = _backend_services.available_fallback_robot_ids(active_task_record["task_id"])
        except ValueError:
            fallback_robot_ids = []
    blocked_reason = None
    if active_task_record:
        blocked_reason = (
            (active_task_record.get("result") or {}).get("reason")
            or dict(active_task_record.get("spec") or {}).get("context", {}).get("failure_reason")
        )
    current_step = None
    current_task_id = None
    if active_task_record:
        current_step = active_task_spec.get("summary")
        current_task_id = active_task_record.get("task_id")
    if current_step is None and active_plan_task:
        current_step = active_plan_task.get("summary")
        current_task_id = active_plan_task.get("task_id")

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
        "currentStep": current_step,
        "currentTaskId": current_task_id,
        "completedSteps": completed_steps,
        "totalSteps": len(plan_tasks),
        "fallbackAvailable": len(fallback_robot_ids) > 0,
        "fallbackRobotIds": fallback_robot_ids,
        "blockedReason": blocked_reason,
        "approvalRequired": bool(approval.get("required", False)),
        "approvalStatus": approval.get("status", "not_required"),
        "replanAvailable": bool(replan),
        "createdAt": session["created_at"],
        "updatedAt": session["updated_at"],
    }


def _mission_events(session: dict) -> list[dict]:
    return list(session.get("metadata", {}).get("mission_events", []))


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
    _backend_services.refresh_mission_sessions()
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


@app.get("/api/tasks/available")
async def get_available_tasks():
    """Get all available task types with their capabilities."""
    return list_available_tasks()


@app.post("/api/tasks/estimate")
async def estimate_task_duration(request: dict):
    """Estimate task execution duration for planning."""
    task_type = request.get("task_type")
    task_spec = request.get("task_spec", {})
    return estimate_task_execution(task_type, task_spec)


@app.post("/api/brain/preview")
async def preview_mission(request: MissionRequest):
    return _mission_brain.preview_mission(
        request.requestText,
        requested_by=request.requestedBy,
        context=request.context,
    )


@app.post("/api/brain/dispatch")
async def dispatch_mission(request: MissionRequest):
    raise HTTPException(
        status_code=409,
        detail="Direct dispatch is disabled. Create a mission preview, approve the validated plan, then dispatch the approved mission.",
    )


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
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    request_record = _build_mission_request_record(
        mission_id,
        request.requestText,
        request.requestedBy,
        request.context,
        submitted_at=now,
        status="submitted",
    )
    proposal = _build_mission_proposal_record(mission_id, result, generated_at=now)
    validated_plan = _build_validated_plan_record(mission_id, result, validated_at=now)
    session = _backend_services.upsert_mission_session(
        mission_id=mission_id,
        request_text=request.requestText,
        requested_by=request.requestedBy,
        status=result["status"],
        preview=result,
        question=result.get("question", {}),
        request_payload=request_record,
        proposal=proposal,
        validated_plan=validated_plan,
        approval=_pending_approval_record(mission_id, required=result["status"] in {"ok", "blocked"}),
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
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    request_record = dict(session.get("request", {}))
    request_record.update(
        _build_mission_request_record(
            mission_id,
            updated_text,
            session["requested_by"],
            context,
            submitted_at=request_record.get("submittedAt") or session["created_at"],
            status="clarified",
        )
    )
    updated = _backend_services.upsert_mission_session(
        mission_id=mission_id,
        request_text=updated_text,
        requested_by=session["requested_by"],
        status=result["status"],
        preview=result,
        question=result.get("question", {}),
        request_payload=request_record,
        proposal=_build_mission_proposal_record(mission_id, result, generated_at=now),
        validated_plan=_build_validated_plan_record(mission_id, result, validated_at=now),
        approval=_pending_approval_record(mission_id, required=result["status"] in {"ok", "blocked"}),
        task_ids=session.get("task_ids", []),
        metadata={"context": context, "intent_provider": result.get("intent_provider")},
        created_at=session["created_at"],
    )
    return {"mission": _mobile_mission_view(updated), "preview": result}


@app.post("/api/mobile/missions/{mission_id}/approve", response_model=MobileMissionDispatchEnvelope)
async def mobile_approve_mission(mission_id: str, request: MissionApprovalRequest):
    session = _backend_services.get_mission_session(mission_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    if session["status"] == "clarification_required":
        raise HTTPException(status_code=409, detail="Mission still requires clarification")
    if session["status"] == "cancelled":
        raise HTTPException(status_code=409, detail="Mission has been cancelled")

    preview = session.get("preview") or {}
    approval = dict(session.get("approval", {}))
    if not preview or preview.get("status") not in {"ok", "blocked"}:
        raise HTTPException(status_code=409, detail="Mission preview is not ready for approval")
    if preview.get("status") == "blocked":
        approval.update(
            {
                "missionId": mission_id,
                "required": True,
                "status": "rejected",
                "decision": "rejected",
                "approvedBy": request.approvedBy,
                "approvedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "notes": "Validated plan is blocked and cannot be dispatched.",
            }
        )
        updated = _backend_services.upsert_mission_session(
            mission_id=mission_id,
            request_text=session["request_text"],
            requested_by=session["requested_by"],
            status="blocked",
            preview=preview,
            question=session.get("question", {}),
            request_payload=session.get("request", {}),
            proposal=session.get("proposal", {}),
            validated_plan=session.get("validated_plan", {}),
            approval=approval,
            task_ids=session.get("task_ids", []),
            metadata={**session.get("metadata", {}), "approved_by": request.approvedBy},
            created_at=session["created_at"],
        )
        return {"mission": _mobile_mission_view(updated), "dispatch": None}

    approval.update(
        {
            "missionId": mission_id,
            "required": True,
            "status": "approved",
            "decision": "approved",
            "approvedBy": request.approvedBy,
            "approvedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "notes": None,
        }
    )
    updated = _backend_services.upsert_mission_session(
        mission_id=mission_id,
        request_text=session["request_text"],
        requested_by=session["requested_by"],
        status="approved",
        preview=preview,
        question={},
        request_payload=session.get("request", {}),
        proposal=session.get("proposal", {}),
        validated_plan=session.get("validated_plan", {}),
        approval=approval,
        task_ids=session.get("task_ids", []),
        metadata={**session.get("metadata", {}), "approved_by": request.approvedBy},
        created_at=session["created_at"],
    )
    return {"mission": _mobile_mission_view(updated), "dispatch": None}


@app.post("/api/mobile/missions/{mission_id}/dispatch", response_model=MobileMissionDispatchEnvelope)
async def mobile_dispatch_mission(mission_id: str, request: MissionConfirmRequest):
    session = _backend_services.get_mission_session(mission_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    if session["status"] in {"clarification_required", "cancelled"}:
        raise HTTPException(status_code=409, detail=f"Mission is {session['status']} and cannot be dispatched")

    preview = session.get("preview") or {}
    approval = dict(session.get("approval") or {})
    validated_plan = dict(session.get("validated_plan") or {})
    if approval.get("status") != "approved":
        raise HTTPException(status_code=409, detail="Mission must be approved before dispatch")
    if not validated_plan.get("executable", preview.get("status") == "ok"):
        raise HTTPException(status_code=409, detail="Validated plan is not executable")

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
        request_payload=session.get("request", {}),
        proposal=session.get("proposal", {}),
        validated_plan=validated_plan,
        approval=approval,
        task_ids=[task["task_id"] for task in dispatch["created_tasks"]],
        metadata={**session.get("metadata", {}), "dispatched_by": request.confirmedBy},
        created_at=session["created_at"],
    )
    refreshed = _backend_services.refresh_mission_sessions()
    updated = next((candidate for candidate in refreshed if candidate["mission_id"] == mission_id), updated)
    return {"mission": _mobile_mission_view(updated), "dispatch": dispatch}


@app.post("/api/mobile/missions/{mission_id}/confirm", response_model=MobileMissionDispatchEnvelope)
async def mobile_confirm_mission(mission_id: str, request: MissionConfirmRequest):
    approval_result = await mobile_approve_mission(mission_id, MissionApprovalRequest(approvedBy=request.confirmedBy))
    mission = approval_result["mission"] if isinstance(approval_result, dict) else approval_result.mission
    if mission.get("status") == "blocked":
        return approval_result
    return await mobile_dispatch_mission(mission_id, request)


@app.get("/api/mobile/missions", response_model=MobileMissionListEnvelope)
async def mobile_list_missions():
    sessions = _backend_services.refresh_mission_sessions()
    return {"missions": [_mobile_mission_view(session) for session in sessions]}


@app.get("/api/mobile/missions/{mission_id}", response_model=MobileMissionDetailEnvelope)
async def mobile_get_mission(mission_id: str):
    _backend_services.refresh_mission_sessions()
    session = _backend_services.get_mission_session(mission_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Mission {mission_id} not found")
    return {
        "mission": _mobile_mission_view(session),
        "preview": session.get("preview", {}),
        "request": session.get("request", {}),
        "proposal": session.get("proposal", {}),
        "validatedPlan": session.get("validated_plan", {}),
        "approval": session.get("approval", {}),
        "replan": session.get("metadata", {}).get("pending_replan") or None,
        "events": _mission_events(session),
    }


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
        request_payload=session.get("request", {}),
        proposal=session.get("proposal", {}),
        validated_plan=session.get("validated_plan", {}),
        approval={**session.get("approval", {}), "status": "cancelled", "decision": "cancelled"},
        task_ids=session.get("task_ids", []),
        metadata=session.get("metadata", {}),
        created_at=session["created_at"],
    )
    return {"mission": _mobile_mission_view(updated), "dispatch": None}


@app.post("/api/mobile/missions/{mission_id}/pause", response_model=MobileMissionDispatchEnvelope)
async def mobile_pause_mission(mission_id: str, request: MissionControlRequest):
    try:
        updated = _backend_services.pause_mission(mission_id, requested_by=request.requestedBy)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"mission": _mobile_mission_view(updated), "dispatch": None}


@app.post("/api/mobile/missions/{mission_id}/resume", response_model=MobileMissionDispatchEnvelope)
async def mobile_resume_mission(mission_id: str, request: MissionControlRequest):
    try:
        updated = _backend_services.resume_mission(mission_id, requested_by=request.requestedBy)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"mission": _mobile_mission_view(updated), "dispatch": None}


@app.post("/api/mobile/missions/{mission_id}/retry", response_model=MobileMissionDispatchEnvelope)
async def mobile_retry_mission(mission_id: str, request: MissionControlRequest):
    try:
        updated = _backend_services.retry_mission(mission_id, requested_by=request.requestedBy)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"mission": _mobile_mission_view(updated), "dispatch": None}


@app.post("/api/mobile/missions/{mission_id}/replan-preview", response_model=MobileMissionDispatchEnvelope)
async def mobile_replan_preview_mission(mission_id: str, request: MissionControlRequest):
    try:
        updated = _backend_services.propose_mission_replan(mission_id, requested_by=request.requestedBy)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"mission": _mobile_mission_view(updated), "dispatch": None}


@app.post("/api/mobile/missions/{mission_id}/replan-apply", response_model=MobileMissionDispatchEnvelope)
async def mobile_replan_apply_mission(mission_id: str, request: MissionControlRequest):
    try:
        updated = _backend_services.apply_mission_replan(mission_id, requested_by=request.requestedBy)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"mission": _mobile_mission_view(updated), "dispatch": None}


@app.post("/api/mobile/missions/{mission_id}/fallback", response_model=MobileMissionDispatchEnvelope)
async def mobile_fallback_mission(mission_id: str, request: MissionControlRequest):
    try:
        updated = _backend_services.use_mission_fallback(mission_id, requested_by=request.requestedBy)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
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
                vendor=config.vendor,
                robot_category=config.robotCategory,
            )
            if not manager.connect():
                raise RuntimeError(
                    f"Robot {config.robotId} could not connect via Unitree SDK on interface {config.networkInterface}"
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


@app.post("/api/backend/tasks/{task_id}/status")
async def set_task_status(task_id: str, request: TaskStatusUpdateRequest):
    try:
        task = _backend_services.set_task_status(task_id, request.status, result=request.result)
        _backend_services.refresh_mission_sessions()
        return {"task": task}
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
            _backend_services.refresh_mission_sessions()
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

# Robot Fleet Configuration API
import sqlite3
from typing import List, Dict, Any

# Robot database path
ROBOT_DB_PATH = "/Users/jeffboggs/robot_fleet/fleet_control/brain/data/robot_fleet.db"

def get_robot_db_connection():
    """Get robot database connection"""
    return sqlite3.connect(ROBOT_DB_PATH)

@app.get("/api/robots/types")
async def get_robot_types():
    """Get all available robot types for fleet configuration"""
    try:
        conn = get_robot_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, manufacturer, model, robot_type, capabilities, specifications,
                   weight_capacity, battery_life_hours, max_speed_kmh, navigation_system,
                   price_amount, availability_status, image_url, documentation_url, data_sheet_url
            FROM robot_types 
            WHERE availability_status = 'available'
            ORDER BY manufacturer, model
        """)
        
        robots = []
        for row in cursor.fetchall():
            robot_data = {
                "id": row[0],
                "manufacturer": row[1],
                "model": row[2],
                "robot_type": row[3],
                "capabilities": json.loads(row[4]),
                "specifications": json.loads(row[5]),
                "weight_capacity": row[6],
                "battery_life_hours": row[7],
                "max_speed_kmh": row[8],
                "navigation_system": row[9],
                "price_amount": row[10],
                "availability_status": row[11],
                "image_url": row[12],
                "documentation_url": row[13],
                "data_sheet_url": row[14]
            }
            robots.append(robot_data)
            
        conn.close()
        return robots
        
    except Exception as e:
        print(f"Error fetching robot types: {e}")
        return []

@app.get("/api/robots/types/{robot_id}")
async def get_robot_type_by_id(robot_id: str):
    """Get detailed information about a specific robot type"""
    try:
        conn = get_robot_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT rt.*, rm.name as manufacturer_name, rm.website as manufacturer_website
            FROM robot_types rt
            JOIN robot_manufacturers rm ON rt.manufacturer_id = rm.id
            WHERE rt.id = ?
        """, (robot_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Robot not found")
            
        robot_data = {
            "id": row[0],
            "manufacturer": row[2],
            "model": row[3],
            "robot_type": row[4],
            "capabilities": json.loads(row[5]),
            "specifications": json.loads(row[6]),
            "weight_capacity": row[7],
            "battery_life_hours": row[8],
            "max_speed_kmh": row[9],
            "navigation_system": row[10],
            "price_amount": row[11],
            "availability_status": row[12],
            "image_url": row[13],
            "documentation_url": row[14],
            "data_sheet_url": row[15]
        }
        
        conn.close()
        return robot_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching robot type: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching robot type: {str(e)}")

@app.get("/api/robots/manufacturers")
async def get_manufacturers():
    """Get all robot manufacturers"""
    try:
        conn = get_robot_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT manufacturer, COUNT(*) as robot_count
            FROM robot_types 
            WHERE availability_status = 'available'
            GROUP BY manufacturer
            ORDER BY manufacturer
        """)
        
        manufacturers = []
        for row in cursor.fetchall():
            manufacturers.append({
                "name": row[0],
                "robot_count": row[1]
            })
            
        conn.close()
        return manufacturers
        
    except Exception as e:
        print(f"Error fetching manufacturers: {e}")
        return []

@app.get("/api/robots/capabilities")
async def get_capabilities():
    """Get all available robot capabilities"""
    try:
        conn = get_robot_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT capabilities
            FROM robot_types 
            WHERE availability_status = 'available'
        """)
        
        all_capabilities = set()
        for row in cursor.fetchall():
            capabilities = json.loads(row[0])
            all_capabilities.update(capabilities)
            
        conn.close()
        
        # Format capabilities with descriptions
        capability_descriptions = {
            "package_delivery": "Deliver packages and goods",
            "navigation": "Autonomous navigation and path planning",
            "obstacle_avoidance": "Detect and avoid obstacles",
            "climbing": "Climb stairs and obstacles",
            "dynamic_balance": "Maintain balance during movement",
            "surveillance": "Monitor and patrol areas",
            "patrol": "Autonomous patrol routes",
            "alert_system": "Send alerts and notifications",
            "human_detection": "Detect human presence",
            "night_vision": "Operate in low light conditions",
            "visual_inspection": "Visual inspection and monitoring",
            "sensor_monitoring": "Monitor environmental sensors",
            "reporting": "Generate inspection reports",
            "thermal_imaging": "Thermal camera imaging",
            "gas_detection": "Detect gas leaks and air quality",
            "diagnostics": "System diagnostics and health checks",
            "repair_assistance": "Assist with maintenance tasks",
            "preventive_maintenance": "Schedule preventive maintenance",
            "tool_carrying": "Carry tools and equipment",
            "remote_operation": "Remote control and operation"
        }
        
        capabilities_list = []
        for capability in sorted(all_capabilities):
            capabilities_list.append({
                "name": capability,
                "description": capability_descriptions.get(capability, f"Capability: {capability}")
            })
            
        return capabilities_list
        
    except Exception as e:
        print(f"Error fetching capabilities: {e}")
        return []

def run_server(controller, port=8000):
    global _fleet_controller
    _fleet_controller = controller
    import uvicorn
    # Important: Run programmatically since we share the controller memory
    print(f"Starting dashboard telemetry server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
