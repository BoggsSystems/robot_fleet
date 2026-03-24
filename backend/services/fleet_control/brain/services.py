"""
Service interfaces for the fleet brain.

These protocols define the seams between intent parsing, planning, policy,
assignment, execution, and learning so the implementation can remain local
first and later gain Azure adapters without rewriting core logic.
"""

from __future__ import annotations

from typing import Protocol

from .domain import (
    ClarificationQuestion,
    ExecutionStatus,
    ExplanationRecord,
    MissionIntent,
    MissionPlan,
    PolicyViolation,
    ResourceSnapshot,
    RobotProfile,
    TaskAssignment,
)


class IntentService(Protocol):
    def parse_request(self, request_text: str, *, requested_by: str, context: dict | None = None) -> MissionIntent | ClarificationQuestion:
        """Convert natural language into a structured mission intent."""


class PolicyEngine(Protocol):
    def validate_mission(self, intent: MissionIntent, resources: ResourceSnapshot | None = None) -> tuple[MissionIntent, tuple[PolicyViolation, ...]]:
        """Validate the intent against hard constraints and return violations."""


class ProposalService(Protocol):
    def build_proposal(self, intent: MissionIntent, resources: ResourceSnapshot) -> dict:
        """Generate a candidate mission proposal before final validation."""


class MissionPlanner(Protocol):
    def build_plan(self, intent: MissionIntent, resources: ResourceSnapshot) -> MissionPlan:
        """Convert a validated mission into a task graph and candidate plan."""


class ResourceAssessmentService(Protocol):
    def assess_resources(self) -> ResourceSnapshot:
        """Return the current allocatable fleet snapshot."""

    def register_robot_profile(self, profile: RobotProfile) -> RobotProfile:
        """Add or update a robot profile in the resource registry."""


class AssignmentEngine(Protocol):
    def assign_plan(self, plan: MissionPlan, resources: ResourceSnapshot) -> tuple[TaskAssignment, ...]:
        """Match planned tasks to robots based on capability and availability."""


class ExecutionSupervisor(Protocol):
    def start_mission(self, plan: MissionPlan) -> ExecutionStatus:
        """Dispatch a mission for execution."""

    def refresh_status(self, mission_id: str) -> ExecutionStatus:
        """Report the current execution status of a mission."""


class ExplanationService(Protocol):
    def summarize_plan(self, plan: MissionPlan, resources: ResourceSnapshot) -> ExplanationRecord:
        """Produce an operator-facing explanation for a plan or assignment."""


class PredictionService(Protocol):
    def estimate_task_duration_minutes(self, task_type: str, *, robot_id: str | None = None, zone_id: str | None = None) -> float | None:
        """Return a learned duration estimate when available."""


class LearningService(Protocol):
    def record_outcome(self, mission_id: str, outcome: dict) -> None:
        """Store execution outcomes for later learning and analysis."""
