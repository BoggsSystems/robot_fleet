"""
Deterministic local implementations of the Phase 2 fleet brain services.

These services keep planning cloud-agnostic and make mission intake testable
against the existing local registry before any Azure adapters are introduced.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Iterable
from uuid import uuid4

from .domain import (
    ClarificationQuestion,
    ExplanationRecord,
    MissionConstraint,
    MissionIntent,
    MissionPlan,
    PlannedTask,
    PolicyViolation,
    ResourceSnapshot,
    RobotProfile,
    TaskAssignment,
    TaskRequirement,
    utc_now_iso,
)
from .openai_intent import OpenAIIntentService
from ..services import FleetBackendServices


class LocalIntentService:
    """Parse simple natural-language requests into structured mission intents."""

    def __init__(self, known_zones: Iterable[str]):
        self._known_zones = tuple(sorted({zone.lower(): zone for zone in known_zones}.values()))

    def parse_request(
        self,
        request_text: str,
        *,
        requested_by: str,
        context: dict | None = None,
    ) -> MissionIntent | ClarificationQuestion:
        normalized = request_text.strip().lower()
        if not normalized:
            return ClarificationQuestion(
                question_id=str(uuid4()),
                mission_id=f"msn-{uuid4().hex[:8]}",
                prompt="What would you like the fleet to do?",
                field_name="objective",
                reason="Request was empty.",
            )

        mission_id = f"msn-{uuid4().hex[:8]}"
        source_zone = _find_zone_after_keywords(normalized, ("from", "at"), self._known_zones)
        destination_zone = _find_zone_after_keywords(normalized, ("to", "into", "inside"), self._known_zones)
        mission_type = _infer_mission_type(normalized)
        cargo_type = _infer_cargo_type(normalized)
        required_capabilities = _infer_capabilities(normalized, mission_type)
        constraints = list(_infer_constraints(normalized))

        if "inside" in normalized and destination_zone is None:
            destination_zone = "kitchen" if "kitchen" in self._known_zones else None

        missing = []
        if mission_type == "cargo_transfer":
            if source_zone is None:
                missing.append("source_zone")
            if destination_zone is None:
                missing.append("destination_zone")
        if missing:
            field_name = missing[0]
            prompt = "Which area should the mission start from?" if field_name == "source_zone" else "Which area should the mission end in?"
            return ClarificationQuestion(
                question_id=str(uuid4()),
                mission_id=mission_id,
                prompt=prompt,
                field_name=field_name,
                reason=f"Could not infer {field_name} from the request.",
            )

        return MissionIntent(
            mission_id=mission_id,
            mission_type=mission_type,
            objective=request_text.strip(),
            requested_by=requested_by,
            source_zone=source_zone,
            destination_zone=destination_zone,
            cargo_type=cargo_type,
            priority=_infer_priority(normalized),
            required_capabilities=tuple(required_capabilities),
            constraints=tuple(constraints),
            human_confirmation_required="as quickly as possible" in normalized or "urgent" in normalized,
            metadata={**(context or {}), "intent_provider": "local-rule-parser"},
        )


class LocalPolicyEngine:
    """Validate mission intent against local deterministic rules."""

    def __init__(self, known_zones: Iterable[str]):
        self._known_zones = {zone.lower() for zone in known_zones}

    def validate_mission(
        self,
        intent: MissionIntent,
        resources: ResourceSnapshot | None = None,
    ) -> tuple[MissionIntent, tuple[PolicyViolation, ...]]:
        violations: list[PolicyViolation] = []

        if intent.source_zone and intent.source_zone.lower() not in self._known_zones:
            violations.append(
                PolicyViolation(
                    code="unknown_source_zone",
                    message=f"Source zone '{intent.source_zone}' is not registered.",
                    severity="error",
                    target="source_zone",
                )
            )
        if intent.destination_zone and intent.destination_zone.lower() not in self._known_zones:
            violations.append(
                PolicyViolation(
                    code="unknown_destination_zone",
                    message=f"Destination zone '{intent.destination_zone}' is not registered.",
                    severity="error",
                    target="destination_zone",
                )
            )
        if intent.source_zone and intent.destination_zone and intent.source_zone.lower() == intent.destination_zone.lower():
            violations.append(
                PolicyViolation(
                    code="invalid_route",
                    message="Source and destination zones must be different.",
                    severity="error",
                    target="mission_route",
                )
            )
        if resources and len(resources.available_robot_ids) == 0:
            violations.append(
                PolicyViolation(
                    code="no_available_resources",
                    message="No robots are currently allocatable for mission planning.",
                    severity="warn",
                    target="resource_snapshot",
                )
            )

        return intent, tuple(violations)


class LocalResourceAssessmentService:
    """Build resource snapshots from the existing persistent robot registry."""

    def __init__(self, backend: FleetBackendServices):
        self._backend = backend

    def assess_resources(self) -> ResourceSnapshot:
        robots = tuple(_profile_from_record(record) for record in self._backend.list_robots())
        available = tuple(
            robot.robot_id
            for robot in robots
            if robot.status in {"idle", "available_soon"} and (robot.battery_level is None or robot.battery_level >= 20.0)
        )
        unavailable = tuple(robot.robot_id for robot in robots if robot.robot_id not in available)
        return ResourceSnapshot(
            snapshot_id=str(uuid4()),
            captured_at=utc_now_iso(),
            robots=robots,
            available_robot_ids=available,
            unavailable_robot_ids=unavailable,
            summary={
                "total_robots": len(robots),
                "available": len(available),
                "unavailable": len(unavailable),
            },
        )

    def register_robot_profile(self, profile: RobotProfile) -> RobotProfile:
        return profile

    def resource_report(self) -> dict:
        snapshot = self.assess_resources()
        robots = []
        for robot in snapshot.robots:
            robots.append(
                {
                    "robot_id": robot.robot_id,
                    "display_name": robot.display_name,
                    "robot_type": robot.robot_type,
                    "model": robot.model,
                    "status": robot.status,
                    "current_zone": robot.current_zone,
                    "battery_level": robot.battery_level,
                    "payload_capacity_kg": robot.payload_capacity_kg,
                    "capabilities": list(robot.capabilities),
                    "allocatable": robot.robot_id in snapshot.available_robot_ids,
                    "reason": _availability_reason(robot),
                }
            )
        return {
            "snapshot": snapshot.to_dict(),
            "robots": robots,
        }


class LocalMissionPlanner:
    """Create a simple task graph from a validated mission intent."""

    def build_plan(self, intent: MissionIntent, resources: ResourceSnapshot) -> MissionPlan:
        tasks = _build_tasks(intent)
        return MissionPlan(
            mission_id=intent.mission_id,
            mission_type=intent.mission_type,
            tasks=tuple(tasks),
            assignments=(),
            unassigned_task_ids=tuple(task.task_id for task in tasks),
            status="validated",
            explanation="Mission validated and translated into a local task graph.",
        )


class LocalAssignmentEngine:
    """Assign planned tasks using deterministic capability matching."""

    def assign_plan(self, plan: MissionPlan, resources: ResourceSnapshot) -> tuple[TaskAssignment, ...]:
        assignments: list[TaskAssignment] = []
        reserved: set[str] = set()
        for task in plan.tasks:
            candidates = [
                robot for robot in resources.robots
                if robot.robot_id in resources.available_robot_ids and robot.robot_id not in reserved and _matches_task(robot, task)
            ]
            if not candidates:
                continue
            candidates.sort(key=lambda robot: (_score_candidate(robot, task), robot.display_name), reverse=True)
            primary = candidates[0]
            reserved.add(primary.robot_id)
            assignments.append(
                TaskAssignment(
                    assignment_id=str(uuid4()),
                    mission_id=plan.mission_id,
                    task_id=task.task_id,
                    robot_id=primary.robot_id,
                    status="proposed",
                    score=round(_score_candidate(primary, task), 3),
                    rationale=_build_rationale(primary, task),
                    fallback_robot_ids=tuple(candidate.robot_id for candidate in candidates[1:3]),
                )
            )
        return tuple(assignments)


class LocalExplanationService:
    def summarize_plan(self, plan: MissionPlan, resources: ResourceSnapshot) -> ExplanationRecord:
        assigned = len(plan.assignments)
        total = len(plan.tasks)
        if assigned == total and total > 0:
            summary = f"All {total} planned tasks have candidate robot assignments."
        elif assigned == 0:
            summary = "No candidate robots were found for the current mission tasks."
        else:
            summary = f"{assigned} of {total} planned tasks have candidate assignments."
        return ExplanationRecord(
            explanation_id=str(uuid4()),
            mission_id=plan.mission_id,
            title="Local mission preview",
            summary=summary,
            details={
                "task_count": total,
                "assignment_count": assigned,
                "available_robots": list(resources.available_robot_ids),
                "unassigned_task_ids": list(plan.unassigned_task_ids),
            },
        )


class LocalMissionBrain:
    """High-level facade for local mission intake and deterministic planning."""

    def __init__(self, backend: FleetBackendServices):
        zones = [zone["zone_id"] for zone in backend.list_zones()] + [zone["name"] for zone in backend.list_zones()]
        self._local_intent = LocalIntentService(zones)
        llm_intent = OpenAIIntentService(zones, fallback=self._local_intent)
        self._intent = llm_intent if llm_intent.enabled else self._local_intent
        self._policy = LocalPolicyEngine(zones)
        self._resources = LocalResourceAssessmentService(backend)
        self._planner = LocalMissionPlanner()
        self._assigner = LocalAssignmentEngine()
        self._explainer = LocalExplanationService()
        self._backend = backend

    def preview_mission(self, request_text: str, *, requested_by: str = "operator@local", context: dict | None = None) -> dict:
        parsed = self._intent.parse_request(request_text, requested_by=requested_by, context=context)
        if isinstance(parsed, ClarificationQuestion):
            return {
                "status": "clarification_required",
                "intent_provider": getattr(self._intent, "provider_label", "local-rule-parser"),
                "question": asdict(parsed),
            }

        resources = self._resources.assess_resources()
        intent, violations = self._policy.validate_mission(parsed, resources)
        plan = self._planner.build_plan(intent, resources)
        assignments = self._assigner.assign_plan(plan, resources)
        assigned_task_ids = {assignment.task_id for assignment in assignments}
        final_plan = MissionPlan(
            mission_id=plan.mission_id,
            mission_type=plan.mission_type,
            tasks=plan.tasks,
            assignments=assignments,
            unassigned_task_ids=tuple(task.task_id for task in plan.tasks if task.task_id not in assigned_task_ids),
            policy_violations=violations,
            status="planned" if not any(v.severity == "error" for v in violations) else "blocked",
            explanation="Mission preview generated by the local deterministic brain.",
        )
        explanation = self._explainer.summarize_plan(final_plan, resources)
        return {
            "status": "ok" if final_plan.status != "blocked" else "blocked",
            "intent_provider": intent.metadata.get("intent_provider", getattr(self._intent, "provider_label", "local-rule-parser")),
            "intent": intent.to_dict(),
            "resources": resources.to_dict(),
            "plan": final_plan.to_dict(),
            "explanation": asdict(explanation),
        }

    def assess_resources(self) -> dict:
        return self._resources.resource_report()

    def reassign_queued_tasks(self) -> dict:
        resources = self._resources.assess_resources()
        queued_tasks = self._backend.list_tasks(status="queued")
        assigned: list[dict] = []
        unassigned: list[dict] = []
        reserved: set[str] = set()

        for record in queued_tasks:
            planned_task = _planned_task_from_record(record)
            candidates = [
                robot
                for robot in resources.robots
                if robot.robot_id in resources.available_robot_ids
                and robot.robot_id not in reserved
                and _matches_task(robot, planned_task)
            ]
            if not candidates:
                unassigned.append(
                    {
                        "task_id": planned_task.task_id,
                        "summary": planned_task.summary,
                        "reason": "No allocatable robot matched current requirements.",
                    }
                )
                continue
            candidates.sort(key=lambda robot: (_score_candidate(robot, planned_task), robot.display_name), reverse=True)
            primary = candidates[0]
            reserved.add(primary.robot_id)
            self._backend.assign_task(planned_task.task_id, primary.robot_id)
            assigned.append(
                {
                    "task_id": planned_task.task_id,
                    "robot_id": primary.robot_id,
                    "score": round(_score_candidate(primary, planned_task), 3),
                    "fallback_robot_ids": [candidate.robot_id for candidate in candidates[1:3]],
                    "rationale": _build_rationale(primary, planned_task),
                }
            )

        return {
            "snapshot": resources.to_dict(),
            "assigned": assigned,
            "unassigned": unassigned,
        }


def _infer_mission_type(text: str) -> str:
    if "inspect" in text or "check" in text:
        return "inspection"
    if "bring" in text or "move" in text or "deliver" in text or "take" in text:
        return "cargo_transfer"
    return "general_assistance"


def _infer_cargo_type(text: str) -> str | None:
    if "grocer" in text:
        return "groceries"
    if "suppl" in text:
        return "supplies"
    return None


def _infer_capabilities(text: str, mission_type: str) -> list[str]:
    capabilities: list[str] = []
    if mission_type == "inspection":
        capabilities.append("inspection")
    if mission_type == "cargo_transfer":
        capabilities.append("cargo_transport")
    if "kitchen" in text or "inside" in text or "indoor" in text:
        capabilities.append("indoor_delivery")
    if "dock" in text or "trail" in text or "outside" in text:
        capabilities.append("outdoor")
    return capabilities


def _infer_constraints(text: str) -> list[MissionConstraint]:
    constraints: list[MissionConstraint] = []
    if "refrigerated" in text or "cold" in text:
        constraints.append(MissionConstraint(key="cold_chain", value=True, severity="warn"))
    if "fragile" in text:
        constraints.append(MissionConstraint(key="fragile", value=True, severity="warn"))
    return constraints


def _infer_priority(text: str):
    if "urgent" in text or "as quickly as possible" in text or "immediately" in text:
        return "urgent"
    if "soon" in text or "priority" in text:
        return "high"
    return "normal"


def _find_zone_after_keywords(text: str, keywords: tuple[str, ...], known_zones: Iterable[str]) -> str | None:
    tokens = text.replace(",", " ").split()
    zone_tokens = {zone.lower(): zone for zone in known_zones}
    for index, token in enumerate(tokens):
        if token not in keywords:
            continue
        for width in (2, 1):
            candidate = " ".join(tokens[index + 1:index + 1 + width]).strip()
            if candidate in zone_tokens:
                return zone_tokens[candidate]
    for zone in known_zones:
        if zone.lower() in text:
            return zone
    return None


def _build_tasks(intent: MissionIntent) -> list[PlannedTask]:
    if intent.mission_type == "inspection":
        return [
            PlannedTask(
                task_id=f"tsk-{uuid4().hex[:8]}",
                mission_id=intent.mission_id,
                task_type="inspection_run",
                summary=f"Inspect {intent.destination_zone or intent.source_zone or 'site'}",
                status="pending",
                requirements=TaskRequirement(
                    required_capabilities=tuple(intent.required_capabilities or ("inspection",)),
                    preferred_robot_types=("quadruped", "drone"),
                    minimum_battery_level=30.0,
                    destination_zone=intent.destination_zone or intent.source_zone,
                ),
                target_zone=intent.destination_zone or intent.source_zone,
                estimated_duration_minutes=10.0,
            )
        ]

    primary = PlannedTask(
        task_id=f"tsk-{uuid4().hex[:8]}",
        mission_id=intent.mission_id,
        task_type="transport",
        summary=f"Move {intent.cargo_type or 'items'} from {intent.source_zone} to {intent.destination_zone}",
        status="pending",
        requirements=TaskRequirement(
            required_capabilities=tuple(intent.required_capabilities),
            preferred_robot_types=("quadruped", "humanoid", "cargo"),
            minimum_battery_level=35.0,
            source_zone=intent.source_zone,
            destination_zone=intent.destination_zone,
            environment="mixed" if intent.source_zone != intent.destination_zone else "indoor",
        ),
        target_zone=intent.destination_zone,
        estimated_duration_minutes=12.0,
    )
    return [primary]


def _planned_task_from_record(record: dict) -> PlannedTask:
    spec = dict(record.get("spec") or {})
    preferred = tuple(spec.get("preferred_robot_types", ("quadruped", "humanoid", "cargo")))
    required = tuple(spec.get("required_capabilities", (record.get("task_type", "general"),)))
    requirements = TaskRequirement(
        required_capabilities=required,
        preferred_robot_types=preferred,
        minimum_battery_level=spec.get("minimum_battery_level", 25.0),
        payload_weight_kg=spec.get("payload_weight_kg"),
        source_zone=spec.get("source_zone") or record.get("zone_id"),
        destination_zone=spec.get("destination_zone"),
        environment=spec.get("environment"),
        supervision_required=bool(spec.get("supervision_required", False)),
        metadata={key: value for key, value in spec.items() if key not in {
            "required_capabilities",
            "preferred_robot_types",
            "minimum_battery_level",
            "payload_weight_kg",
            "source_zone",
            "destination_zone",
            "environment",
            "supervision_required",
        }},
    )
    return PlannedTask(
        task_id=record["task_id"],
        mission_id=spec.get("mission_id", record["task_id"]),
        task_type=record["task_type"],
        summary=spec.get("summary", record["task_type"].replace("_", " ").title()),
        status="pending",
        requirements=requirements,
        target_zone=requirements.destination_zone or requirements.source_zone,
        estimated_duration_minutes=spec.get("estimated_duration_minutes"),
        metadata=spec,
    )


def _profile_from_record(record: dict) -> RobotProfile:
    metadata = dict(record.get("metadata") or {})
    battery = metadata.get("battery_level")
    if battery is None:
        battery = 100.0 if record.get("status") in {"idle", "available_soon"} else 65.0
    payload = metadata.get("payload_capacity_kg")
    if payload is None:
        payload = _default_payload_for_category(record.get("robot_category", ""))
    return RobotProfile(
        robot_id=record["robot_id"],
        display_name=record.get("name", record["robot_id"]),
        robot_type=_normalize_robot_type(record.get("robot_category"), record.get("robot_type")),
        model=record.get("model", record.get("robot_type", "Unknown")),
        capabilities=tuple(record.get("capabilities", [])),
        status=_normalize_status(record.get("status", "idle")),
        location=record.get("site_id") or "Cottage",
        current_zone=record.get("zone_id") or "site",
        battery_level=float(battery) if battery is not None else None,
        payload_capacity_kg=float(payload) if payload is not None else None,
        range_minutes=metadata.get("range_minutes"),
        constraints=tuple(metadata.get("constraints", [])),
        metadata=metadata,
    )


def _normalize_robot_type(category: str | None, robot_type: str | None):
    normalized = f"{category or ''} {robot_type or ''}".lower()
    if "quad" in normalized or "go2" in normalized or "go4" in normalized:
        return "quadruped"
    if "human" in normalized or "g1" in normalized or "r1" in normalized:
        return "humanoid"
    if "cargo" in normalized:
        return "cargo"
    if "drone" in normalized:
        return "drone"
    if "boat" in normalized:
        return "boat"
    return "unknown"


def _normalize_status(status: str):
    normalized = status.lower()
    if normalized in {"idle", "available_soon", "busy", "charging", "degraded", "maintenance", "offline", "reserved"}:
        return normalized
    if normalized in {"active", "assigned", "running"}:
        return "busy"
    return "idle"


def _availability_reason(robot: RobotProfile) -> str:
    if robot.status in {"offline", "maintenance"}:
        return f"Excluded: robot is {robot.status}."
    if robot.status in {"busy", "reserved"}:
        return f"Held: robot is currently {robot.status}."
    if robot.status == "charging":
        return "Deferred: robot is charging."
    if robot.status == "degraded":
        return "Caution: robot is degraded and requires review."
    if robot.battery_level is not None and robot.battery_level < 20.0:
        return f"Deferred: battery is {robot.battery_level:.0f}%."
    return "Allocatable now."


def _default_payload_for_category(category: str) -> float | None:
    normalized = category.lower()
    if "quad" in normalized:
        return 12.5
    if "human" in normalized:
        return 8.0
    if "cargo" in normalized:
        return 30.0
    return None


def _matches_task(robot: RobotProfile, task: PlannedTask) -> bool:
    req = task.requirements
    if req.minimum_battery_level is not None and robot.battery_level is not None and robot.battery_level < req.minimum_battery_level:
        return False
    if req.payload_weight_kg is not None and robot.payload_capacity_kg is not None and req.payload_weight_kg > robot.payload_capacity_kg:
        return False
    if req.preferred_robot_types and robot.robot_type not in req.preferred_robot_types:
        return False
    if any(cap not in robot.capabilities for cap in req.required_capabilities):
        return False
    return True


def _score_candidate(robot: RobotProfile, task: PlannedTask) -> float:
    score = 0.0
    if robot.battery_level is not None:
        score += robot.battery_level / 100.0
    if robot.current_zone == task.requirements.source_zone:
        score += 0.4
    if robot.robot_type in task.requirements.preferred_robot_types:
        score += 0.3
    score += min(len(set(robot.capabilities) & set(task.requirements.required_capabilities)) * 0.1, 0.3)
    return score


def _build_rationale(robot: RobotProfile, task: PlannedTask) -> str:
    reasons = [f"{robot.display_name} is {robot.status}"]
    if robot.current_zone == task.requirements.source_zone:
        reasons.append(f"already positioned at {robot.current_zone}")
    if robot.payload_capacity_kg is not None:
        reasons.append(f"payload capacity {robot.payload_capacity_kg:.1f}kg")
    if robot.battery_level is not None:
        reasons.append(f"battery {robot.battery_level:.0f}%")
    return ", ".join(reasons) + "."
