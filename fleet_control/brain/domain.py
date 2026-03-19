"""
Cloud-agnostic domain contracts for the fleet "brain".

These dataclasses define the canonical request/response shapes for mission
intake, planning, assignment, supervision, and explanation before any Azure
adapter or concrete planner implementation exists.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4


MissionPriority = Literal["low", "normal", "high", "urgent"]
MissionStatus = Literal["draft", "validated", "planned", "dispatched", "running", "completed", "blocked", "cancelled"]
TaskStatus = Literal["pending", "assigned", "dispatched", "running", "completed", "blocked", "failed"]
AssignmentStatus = Literal["proposed", "reserved", "dispatched", "rejected", "completed"]
RobotAvailability = Literal["idle", "available_soon", "busy", "charging", "degraded", "maintenance", "offline", "reserved"]
RobotType = Literal["humanoid", "cargo", "quadruped", "drone", "boat", "unknown"]
ConstraintSeverity = Literal["info", "warn", "error"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class MissionConstraint:
    key: str
    value: Any
    severity: ConstraintSeverity = "info"


@dataclass(frozen=True)
class MissionIntent:
    mission_id: str
    mission_type: str
    objective: str
    requested_by: str
    source_zone: str | None = None
    destination_zone: str | None = None
    cargo_type: str | None = None
    priority: MissionPriority = "normal"
    required_capabilities: tuple[str, ...] = ()
    constraints: tuple[MissionConstraint, ...] = ()
    time_window: dict[str, str] | None = None
    human_confirmation_required: bool = False
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ClarificationQuestion:
    question_id: str
    mission_id: str
    prompt: str
    field_name: str
    reason: str


@dataclass(frozen=True)
class RobotProfile:
    robot_id: str
    display_name: str
    robot_type: RobotType
    model: str
    capabilities: tuple[str, ...]
    status: RobotAvailability
    location: str
    current_zone: str
    battery_level: float | None
    payload_capacity_kg: float | None
    range_minutes: int | None = None
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskRequirement:
    required_capabilities: tuple[str, ...] = ()
    preferred_robot_types: tuple[RobotType, ...] = ()
    minimum_battery_level: float | None = None
    payload_weight_kg: float | None = None
    source_zone: str | None = None
    destination_zone: str | None = None
    environment: str | None = None
    supervision_required: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlannedTask:
    task_id: str
    mission_id: str
    task_type: str
    summary: str
    status: TaskStatus
    requirements: TaskRequirement
    depends_on: tuple[str, ...] = ()
    target_zone: str | None = None
    estimated_duration_minutes: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyViolation:
    code: str
    message: str
    severity: ConstraintSeverity
    target: str


@dataclass(frozen=True)
class ResourceSnapshot:
    snapshot_id: str
    captured_at: str
    robots: tuple[RobotProfile, ...]
    available_robot_ids: tuple[str, ...]
    unavailable_robot_ids: tuple[str, ...]
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TaskAssignment:
    assignment_id: str
    mission_id: str
    task_id: str
    robot_id: str
    status: AssignmentStatus
    score: float | None = None
    rationale: str = ""
    fallback_robot_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class MissionPlan:
    mission_id: str
    mission_type: str
    tasks: tuple[PlannedTask, ...]
    assignments: tuple[TaskAssignment, ...]
    unassigned_task_ids: tuple[str, ...] = ()
    policy_violations: tuple[PolicyViolation, ...] = ()
    status: MissionStatus = "draft"
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExecutionStatus:
    mission_id: str
    status: MissionStatus
    active_task_id: str | None
    completed_task_ids: tuple[str, ...]
    blocked_task_ids: tuple[str, ...]
    updated_at: str = field(default_factory=utc_now_iso)
    notes: str = ""


@dataclass(frozen=True)
class ExplanationRecord:
    explanation_id: str
    mission_id: str
    title: str
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now_iso)


def make_sample_phase1_contracts() -> dict[str, Any]:
    mission_id = "msn-grocery-demo"
    robot = RobotProfile(
        robot_id="carrier-01",
        display_name="Carrier 01",
        robot_type="quadruped",
        model="Unitree Go2",
        capabilities=("cargo_transport", "rough_terrain", "outdoor"),
        status="idle",
        location="Cottage",
        current_zone="dock",
        battery_level=84.0,
        payload_capacity_kg=12.5,
        range_minutes=55,
    )
    intent = MissionIntent(
        mission_id=mission_id,
        mission_type="cargo_transfer",
        objective="Bring groceries from dock to kitchen",
        requested_by="operator@local",
        source_zone="dock",
        destination_zone="kitchen",
        cargo_type="groceries",
        required_capabilities=("cargo_transport", "indoor_delivery"),
        constraints=(
            MissionConstraint(key="cold_chain", value=False),
            MissionConstraint(key="priority", value="normal"),
        ),
    )
    task = PlannedTask(
        task_id="tsk-grocery-01",
        mission_id=mission_id,
        task_type="pickup_and_deliver",
        summary="Move grocery load from dock to kitchen staging",
        status="pending",
        requirements=TaskRequirement(
            required_capabilities=("cargo_transport",),
            preferred_robot_types=("quadruped", "humanoid"),
            minimum_battery_level=35.0,
            source_zone="dock",
            destination_zone="kitchen",
        ),
        target_zone="kitchen",
        estimated_duration_minutes=12.0,
    )
    assignment = TaskAssignment(
        assignment_id=str(uuid4()),
        mission_id=mission_id,
        task_id=task.task_id,
        robot_id=robot.robot_id,
        status="proposed",
        score=0.92,
        rationale="Quadruped is idle at dock with sufficient payload capacity.",
        fallback_robot_ids=("carrier-02",),
    )
    plan = MissionPlan(
        mission_id=mission_id,
        mission_type=intent.mission_type,
        tasks=(task,),
        assignments=(assignment,),
        status="planned",
        explanation="Mission parsed and candidate assignment prepared for review.",
    )
    snapshot = ResourceSnapshot(
        snapshot_id=str(uuid4()),
        captured_at=utc_now_iso(),
        robots=(robot,),
        available_robot_ids=(robot.robot_id,),
        unavailable_robot_ids=(),
        summary={"total_robots": 1, "available": 1},
    )
    explanation = ExplanationRecord(
        explanation_id=str(uuid4()),
        mission_id=mission_id,
        title="Candidate assignment",
        summary="Carrier 01 is the best current candidate for the grocery transfer.",
        details={"score": assignment.score, "fallbacks": assignment.fallback_robot_ids},
    )
    return {
        "intent": intent.to_dict(),
        "resource_snapshot": snapshot.to_dict(),
        "plan": plan.to_dict(),
        "execution_status": asdict(
            ExecutionStatus(
                mission_id=mission_id,
                status="planned",
                active_task_id=None,
                completed_task_ids=(),
                blocked_task_ids=(),
                notes="Awaiting human confirmation.",
            )
        ),
        "explanation": asdict(explanation),
    }
