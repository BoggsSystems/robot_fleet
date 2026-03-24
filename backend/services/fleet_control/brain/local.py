"""
Deterministic local implementations of the Phase 2 fleet brain services.

These services keep planning cloud-agnostic and make mission intake testable
against the existing local registry before any Azure adapters are introduced.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable
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
from .openai_proposal import OpenAIProposalService
from ..services import FleetBackendServices
from ..site_graph import load_default_site_graph


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
        if intent.mission_type == "cargo_transfer" and not intent.required_capabilities:
            violations.append(
                PolicyViolation(
                    code="missing_capabilities",
                    message="Cargo transfer missions must resolve at least one required capability.",
                    severity="error",
                    target="required_capabilities",
                )
            )
        if resources:
            eligible = [robot for robot in resources.robots if _robot_can_support_intent(robot, intent)]
            if not eligible:
                violations.append(
                    PolicyViolation(
                        code="no_capable_robot",
                        message="No registered robot currently matches the mission's capability and readiness requirements.",
                        severity="error",
                        target="resource_snapshot",
                    )
                )
            elif intent.priority == "urgent" and not any(robot.status == "idle" for robot in eligible):
                violations.append(
                    PolicyViolation(
                        code="urgent_capacity_limited",
                        message="Urgent mission has no immediately idle preferred robot; expect delayed execution.",
                        severity="warn",
                        target="resource_snapshot",
                    )
                )
            if _has_constraint(intent, "cold_chain") and not any(
                (robot.battery_level or 0.0) >= 45.0 and (robot.payload_capacity_kg or 0.0) >= 5.0
                for robot in eligible
            ):
                violations.append(
                    PolicyViolation(
                        code="cold_chain_risk",
                        message="Cold-chain handling is possible, but no robot currently has strong battery headroom for a protected transfer window.",
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
            explanation=_plan_summary(intent, tasks),
        )


class LocalProposalService:
    """Generate a candidate operator-facing plan before final validation."""

    provider_label = "local-proposal"

    def __init__(self, backend: FleetBackendServices):
        self._backend = backend

    def build_proposal(self, intent: MissionIntent, resources: ResourceSnapshot) -> dict[str, Any]:
        site_graph = self._backend.get_site_graph()
        tasks = _build_tasks(intent)
        candidate_steps = [_proposal_step(task, resources, site_graph) for task in tasks]
        warnings: list[str] = []
        if not resources.available_robot_ids:
            warnings.append("No robots are allocatable right now.")
        if _has_constraint(intent, "cold_chain"):
            warnings.append("Cold-chain handling requires a tighter transfer window.")
        for step in candidate_steps:
            if not step["candidate_allocations"]:
                warnings.append(f"No candidate robot is currently available for '{step['summary']}'.")
        assumptions = _proposal_assumptions(intent, resources, site_graph)
        return {
            "mission_id": intent.mission_id,
            "provider": self.provider_label,
            "mission_type": intent.mission_type,
            "objective": intent.objective,
            "status": "candidate",
            "plan_summary": _plan_summary(intent, tasks, site_graph),
            "assumptions": assumptions,
            "warnings": warnings,
            "operator_notes": _proposal_operator_notes(tasks, site_graph),
            "candidate_steps": candidate_steps,
            "generated_at": utc_now_iso(),
        }


class LocalAssignmentEngine:
    """Assign planned tasks using deterministic capability matching."""

    def assign_plan(self, plan: MissionPlan, resources: ResourceSnapshot) -> tuple[TaskAssignment, ...]:
        assignments: list[TaskAssignment] = []
        reserved: set[str] = set()
        group_assignments: dict[str, TaskAssignment] = {}
        for task in plan.tasks:
            assignment_group = str(task.metadata.get("assignment_group", "")).strip()
            grouped = group_assignments.get(assignment_group) if assignment_group else None
            if grouped is not None:
                grouped_robot = next((robot for robot in resources.robots if robot.robot_id == grouped.robot_id), None)
                if grouped_robot is not None and _matches_task(grouped_robot, task):
                    assignments.append(
                        TaskAssignment(
                            assignment_id=str(uuid4()),
                            mission_id=plan.mission_id,
                            task_id=task.task_id,
                            robot_id=grouped_robot.robot_id,
                            status="proposed",
                            score=round(_score_candidate(grouped_robot, task), 3),
                            rationale=f"{_build_rationale(grouped_robot, task)} Reusing the same robot for the {assignment_group.replace('_', ' ')} sequence.",
                            fallback_robot_ids=grouped.fallback_robot_ids,
                        )
                    )
                    continue
            candidates = [
                robot for robot in resources.robots
                if robot.robot_id in resources.available_robot_ids and robot.robot_id not in reserved and _matches_task(robot, task)
            ]
            if not candidates:
                continue
            candidates.sort(key=lambda robot: (_score_candidate(robot, task), robot.display_name), reverse=True)
            primary = candidates[0]
            reserved.add(primary.robot_id)
            assignment = TaskAssignment(
                assignment_id=str(uuid4()),
                mission_id=plan.mission_id,
                task_id=task.task_id,
                robot_id=primary.robot_id,
                status="proposed",
                score=round(_score_candidate(primary, task), 3),
                rationale=_build_rationale(primary, task),
                fallback_robot_ids=tuple(candidate.robot_id for candidate in candidates[1:4]),
            )
            assignments.append(assignment)
            if assignment_group:
                group_assignments[assignment_group] = assignment
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
                "policy_violations": [asdict(violation) for violation in plan.policy_violations],
                "assignments": [asdict(assignment) for assignment in plan.assignments],
            },
        )


class LocalValidatedPlanService:
    """Build an executable validated-plan record from tasks, assignments, and site structure."""

    def __init__(self, backend: FleetBackendServices):
        self._backend = backend

    def build_validated_plan(
        self,
        intent: MissionIntent,
        resources: ResourceSnapshot,
        plan: MissionPlan,
    ) -> dict[str, Any]:
        site_graph = self._backend.get_site_graph()
        zone_index = {
            node.node_id.lower(): node.raw
            for node in site_graph.nodes.values()
        }
        assignments_by_task = {assignment.task_id: assignment for assignment in plan.assignments}
        plan_task_ids = {task.task_id for task in plan.tasks}

        validation_checks: list[dict[str, Any]] = []
        warnings: list[str] = []
        blocking_reasons: list[str] = []

        for task in plan.tasks:
            source_zone = (task.requirements.source_zone or "").lower()
            destination_zone = (task.requirements.destination_zone or "").lower()
            resolved_source = site_graph.resolve_node_id(task.requirements.source_zone)
            resolved_destination = site_graph.resolve_node_id(task.requirements.destination_zone)
            if source_zone and not resolved_source:
                blocking_reasons.append(f"Task '{task.summary}' references unknown source zone '{task.requirements.source_zone}'.")
            if destination_zone and not resolved_destination:
                blocking_reasons.append(f"Task '{task.summary}' references unknown destination zone '{task.requirements.destination_zone}'.")
            if source_zone and destination_zone:
                route = site_graph.route_between(task.requirements.source_zone, task.requirements.destination_zone)
                route_ok = route is not None
                validation_checks.append(
                    {
                        "task_id": task.task_id,
                        "check": "route_feasibility",
                        "passed": route_ok,
                        "route": route or [],
                        "route_labels": site_graph.route_labels(route),
                    }
                )
                if not route_ok:
                    blocking_reasons.append(
                        f"No known route connects {task.requirements.source_zone} to {task.requirements.destination_zone} for '{task.summary}'."
                    )
                elif _is_exterior_zone(task.requirements.source_zone) and _is_interior_zone(task.requirements.destination_zone) and "entry" not in route:
                    warnings.append(f"'{task.summary}' crosses exterior to interior without an explicit entry handoff in the site graph.")

            missing_dependencies = [dependency for dependency in task.depends_on if dependency not in plan_task_ids]
            validation_checks.append(
                {
                    "task_id": task.task_id,
                    "check": "dependency_integrity",
                    "passed": len(missing_dependencies) == 0,
                    "missing_dependencies": missing_dependencies,
                }
            )
            if missing_dependencies:
                blocking_reasons.append(f"Task '{task.summary}' has missing dependencies: {', '.join(missing_dependencies)}.")

            assignment = assignments_by_task.get(task.task_id)
            assignment_ok = assignment is not None
            validation_checks.append(
                {
                    "task_id": task.task_id,
                    "check": "assignment_coverage",
                    "passed": assignment_ok,
                    "robot_id": assignment.robot_id if assignment else None,
                }
            )
            if not assignment_ok:
                blocking_reasons.append(f"Task '{task.summary}' has no allocatable robot candidate.")
            elif not assignment.fallback_robot_ids:
                warnings.append(f"Task '{task.summary}' has no configured fallback robot.")

        blocked = any(violation.severity == "error" for violation in plan.policy_violations) or bool(blocking_reasons)
        status = "blocked" if blocked else "planned"
        validation_summary = {
            "total_tasks": len(plan.tasks),
            "assigned_tasks": len(plan.assignments),
            "available_robot_count": len(resources.available_robot_ids),
            "warning_count": len(warnings),
            "blocking_count": len(blocking_reasons),
        }

        validated = plan.to_dict()
        validated.update(
            {
                "status": status,
                "warnings": warnings,
                "blocking_reasons": blocking_reasons,
                "validation_checks": validation_checks,
                "validation_summary": validation_summary,
                "site_graph_context": {
                    "known_zones": sorted(node.label for node in site_graph.nodes.values()),
                    "route_basis": str(site_graph.source_path),
                    "intent_source_zone": intent.source_zone,
                    "intent_destination_zone": intent.destination_zone,
                },
            }
        )
        return validated


class LocalMissionBrain:
    """High-level facade for local mission intake and deterministic planning."""

    def __init__(self, backend: FleetBackendServices):
        site_graph = backend.get_site_graph() if hasattr(backend, "get_site_graph") else load_default_site_graph()
        zones = [zone["zone_id"] for zone in backend.list_zones()] + [zone["name"] for zone in backend.list_zones()]
        zones.extend(site_graph.known_zone_terms())
        self._local_intent = LocalIntentService(zones)
        llm_intent = OpenAIIntentService(zones, fallback=self._local_intent)
        self._intent = llm_intent if llm_intent.enabled else self._local_intent
        self._policy = LocalPolicyEngine(zones)
        self._resources = LocalResourceAssessmentService(backend)
        self._local_proposal = LocalProposalService(backend)
        llm_proposal = OpenAIProposalService(self._local_proposal)
        self._proposal = llm_proposal if llm_proposal.enabled else self._local_proposal
        self._planner = LocalMissionPlanner()
        self._assigner = LocalAssignmentEngine()
        self._validator = LocalValidatedPlanService(backend)
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
        proposal = self._proposal.build_proposal(parsed, resources)
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
            status="planned",
            explanation=_final_plan_explanation(plan.tasks, assignments, violations),
        )
        validated_plan = self._validator.build_validated_plan(intent, resources, final_plan)
        explanation = self._explainer.summarize_plan(
            MissionPlan(
                mission_id=final_plan.mission_id,
                mission_type=final_plan.mission_type,
                tasks=final_plan.tasks,
                assignments=final_plan.assignments,
                unassigned_task_ids=final_plan.unassigned_task_ids,
                policy_violations=final_plan.policy_violations,
                status=validated_plan["status"],
                explanation=validated_plan.get("explanation", final_plan.explanation),
            ),
            resources,
        )
        return {
            "status": "ok" if validated_plan["status"] != "blocked" else "blocked",
            "intent_provider": intent.metadata.get("intent_provider", getattr(self._intent, "provider_label", "local-rule-parser")),
            "intent": intent.to_dict(),
            "resources": resources.to_dict(),
            "proposal": proposal,
            "plan": validated_plan,
            "validated_plan": validated_plan,
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

    return _build_cargo_tasks(intent)


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
    if req.environment == "indoor" and "indoor_delivery" not in robot.capabilities:
        return False
    if req.environment == "outdoor" and "outdoor" not in robot.capabilities:
        return False
    if req.supervision_required and "human_supervised" in robot.constraints:
        return False
    if task.estimated_duration_minutes is not None and robot.range_minutes is not None and robot.range_minutes < max(task.estimated_duration_minutes * 1.2, 10.0):
        return False
    return True


def _score_candidate(robot: RobotProfile, task: PlannedTask) -> float:
    score = 0.0
    if robot.battery_level is not None:
        score += min(robot.battery_level / 100.0, 1.0)
    if robot.current_zone == task.requirements.source_zone:
        score += 0.45
    elif robot.current_zone == task.requirements.destination_zone:
        score += 0.15
    if robot.robot_type in task.requirements.preferred_robot_types:
        score += 0.3
    score += min(len(set(robot.capabilities) & set(task.requirements.required_capabilities)) * 0.12, 0.36)
    if task.requirements.payload_weight_kg is not None and robot.payload_capacity_kg is not None:
        headroom = robot.payload_capacity_kg - task.requirements.payload_weight_kg
        if headroom >= 0:
            score += min(headroom / 40.0, 0.2)
    if task.estimated_duration_minutes is not None and robot.range_minutes is not None:
        range_margin = robot.range_minutes - task.estimated_duration_minutes
        score += max(min(range_margin / 120.0, 0.15), -0.2)
    if task.requirements.environment == "indoor" and "fine_manipulation" in robot.capabilities:
        score += 0.08
    if robot.status == "available_soon":
        score -= 0.15
    if robot.status == "degraded":
        score -= 0.25
    return score


def _build_rationale(robot: RobotProfile, task: PlannedTask) -> str:
    reasons = [f"{robot.display_name} is {robot.status}"]
    if robot.current_zone == task.requirements.source_zone:
        reasons.append(f"already positioned at {robot.current_zone}")
    if robot.payload_capacity_kg is not None:
        reasons.append(f"payload capacity {robot.payload_capacity_kg:.1f}kg")
    if robot.battery_level is not None:
        reasons.append(f"battery {robot.battery_level:.0f}%")
    if task.requirements.environment == "indoor" and "fine_manipulation" in robot.capabilities:
        reasons.append("fine manipulation available for indoor handoff")
    if robot.range_minutes is not None and task.estimated_duration_minutes is not None:
        reasons.append(f"range margin {max(robot.range_minutes - task.estimated_duration_minutes, 0):.0f} min")
    return ", ".join(reasons) + "."


def _proposal_step(task: PlannedTask, resources: ResourceSnapshot, site_graph) -> dict[str, Any]:
    candidates = [
        robot
        for robot in resources.robots
        if robot.robot_id in resources.available_robot_ids and _matches_task(robot, task)
    ]
    candidates.sort(key=lambda robot: (_score_candidate(robot, task), robot.display_name), reverse=True)
    route = site_graph.route_between(task.requirements.source_zone, task.requirements.destination_zone)
    return {
        "task_id": task.task_id,
        "summary": task.summary,
        "task_type": task.task_type,
        "depends_on": list(task.depends_on),
        "target_zone": task.target_zone,
        "estimated_duration_minutes": task.estimated_duration_minutes,
        "route_labels": site_graph.route_labels(route),
        "requirements": asdict(task.requirements),
        "candidate_allocations": [
            {
                "robot_id": robot.robot_id,
                "display_name": robot.display_name,
                "robot_type": robot.robot_type,
                "score": round(_score_candidate(robot, task), 3),
                "rationale": _build_rationale(robot, task),
            }
            for robot in candidates[:3]
        ],
    }


def _proposal_assumptions(intent: MissionIntent, resources: ResourceSnapshot, site_graph) -> list[str]:
    assumptions: list[str] = []
    if intent.source_zone and intent.destination_zone:
        route = site_graph.route_between(intent.source_zone, intent.destination_zone)
        route_labels = site_graph.route_labels(route)
        if route_labels:
            assumptions.append(f"Primary route uses: {' -> '.join(route_labels)}.")
        assumptions.append(f"Route from {intent.source_zone} to {intent.destination_zone} remains traversable.")
    if intent.mission_type == "cargo_transfer":
        assumptions.append("Cargo is staged and accessible for pickup at the source zone.")
    if resources.available_robot_ids:
        assumptions.append("At least one currently allocatable robot remains available through dispatch.")
    return assumptions


def _proposal_operator_notes(tasks: list[PlannedTask], site_graph) -> list[str]:
    notes: list[str] = []
    for task in tasks:
        route = site_graph.route_between(task.requirements.source_zone, task.requirements.destination_zone)
        route_labels = site_graph.route_labels(route)
        if route_labels and len(route_labels) > 2:
            notes.append(f"{task.summary} crosses {len(route_labels)} operational nodes.")
        if "entry" in (task.requirements.destination_zone or "").lower():
            notes.append("Entry foyer is the preferred handoff threshold between exterior transport and interior delivery.")
        if task.requirements.environment == "outdoor":
            notes.append("Outdoor segments should account for dock footing, narrow walkway width, and natural-path obstacles.")
        if task.requirements.environment == "indoor":
            notes.append("Indoor delivery should respect the foyer-to-dining-room transition and kitchen access path.")
    return list(dict.fromkeys(notes))


def _build_cargo_tasks(intent: MissionIntent) -> list[PlannedTask]:
    cargo_name = intent.cargo_type or "items"
    source_zone = intent.source_zone
    destination_zone = intent.destination_zone
    is_crossing_environments = _is_exterior_zone(source_zone) and _is_interior_zone(destination_zone)
    cold_chain = _has_constraint(intent, "cold_chain")
    payload_weight = 10.0 if cargo_name == "groceries" else 6.0

    if not is_crossing_environments:
        return [
            PlannedTask(
                task_id=f"tsk-{uuid4().hex[:8]}",
                mission_id=intent.mission_id,
                task_type="transport",
                summary=f"Move {cargo_name} from {source_zone} to {destination_zone}",
                status="pending",
                requirements=TaskRequirement(
                    required_capabilities=tuple(intent.required_capabilities),
                    preferred_robot_types=("quadruped", "humanoid", "cargo"),
                    minimum_battery_level=40.0 if cold_chain else 35.0,
                    payload_weight_kg=payload_weight,
                    source_zone=source_zone,
                    destination_zone=destination_zone,
                    environment=_task_environment(source_zone, destination_zone),
                    metadata={"temperature_sensitive": cold_chain},
                ),
                target_zone=destination_zone,
                estimated_duration_minutes=10.0 if not cold_chain else 8.0,
                metadata={"step_index": 1, "assignment_group": "direct_transfer"},
            )
        ]

    pickup_id = f"tsk-{uuid4().hex[:8]}"
    transfer_id = f"tsk-{uuid4().hex[:8]}"
    delivery_id = f"tsk-{uuid4().hex[:8]}"

    return [
        PlannedTask(
            task_id=pickup_id,
            mission_id=intent.mission_id,
            task_type="pickup",
            summary=f"Stage {cargo_name} at {source_zone} for transfer",
            status="pending",
            requirements=TaskRequirement(
                required_capabilities=("cargo_transport", "outdoor"),
                preferred_robot_types=("quadruped", "cargo"),
                minimum_battery_level=32.0,
                payload_weight_kg=payload_weight,
                source_zone=source_zone,
                destination_zone=source_zone,
                environment="outdoor",
                metadata={"temperature_sensitive": cold_chain},
            ),
            target_zone=source_zone,
            estimated_duration_minutes=4.0,
            metadata={"step_index": 1, "assignment_group": "exterior_transfer"},
        ),
        PlannedTask(
            task_id=transfer_id,
            mission_id=intent.mission_id,
            task_type="transport",
            summary=f"Transfer {cargo_name} from {source_zone} to entry",
            status="pending",
            requirements=TaskRequirement(
                required_capabilities=("cargo_transport", "outdoor"),
                preferred_robot_types=("quadruped", "cargo"),
                minimum_battery_level=40.0 if cold_chain else 35.0,
                payload_weight_kg=payload_weight,
                source_zone=source_zone,
                destination_zone="entry",
                environment="mixed",
                metadata={"temperature_sensitive": cold_chain},
            ),
            depends_on=(pickup_id,),
            target_zone="entry",
            estimated_duration_minutes=7.0,
            metadata={"step_index": 2, "assignment_group": "exterior_transfer"},
        ),
        PlannedTask(
            task_id=delivery_id,
            mission_id=intent.mission_id,
            task_type="handoff_delivery",
            summary=f"Complete indoor delivery of {cargo_name} to {destination_zone}",
            status="pending",
            requirements=TaskRequirement(
                required_capabilities=("indoor_delivery",) + (("fine_manipulation",) if cargo_name == "groceries" else ()),
                preferred_robot_types=("humanoid", "quadruped"),
                minimum_battery_level=28.0,
                payload_weight_kg=max(payload_weight - 2.0, 2.0),
                source_zone="entry",
                destination_zone=destination_zone,
                environment="indoor",
                metadata={"temperature_sensitive": cold_chain},
            ),
            depends_on=(transfer_id,),
            target_zone=destination_zone,
            estimated_duration_minutes=6.0,
            metadata={"step_index": 3, "assignment_group": "interior_delivery"},
        ),
    ]


def _plan_summary(intent: MissionIntent, tasks: list[PlannedTask], site_graph=None) -> str:
    if site_graph and intent.source_zone and intent.destination_zone:
        route = site_graph.route_between(intent.source_zone, intent.destination_zone)
        route_labels = site_graph.route_labels(route)
        if route_labels:
            return f"Mission uses the authored site route: {' -> '.join(route_labels)}."
    if intent.mission_type == "cargo_transfer" and len(tasks) > 1:
        return f"Mission decomposed into {len(tasks)} staged tasks covering pickup, transfer, and final delivery."
    return "Mission validated and translated into a local task graph."


def _final_plan_explanation(
    tasks: tuple[PlannedTask, ...],
    assignments: tuple[TaskAssignment, ...],
    violations: tuple[PolicyViolation, ...],
) -> str:
    if any(violation.severity == "error" for violation in violations):
        return "Mission preview is blocked until the reported policy issues are resolved."
    if not tasks:
        return "Mission preview did not generate executable tasks."
    if not assignments:
        return "Mission preview generated tasks, but no allocatable robot matched the current requirements."
    if len(assignments) == len(tasks):
        return f"Mission preview generated {len(tasks)} staged tasks with candidate robots for each step."
    return f"Mission preview generated {len(tasks)} staged tasks, but only {len(assignments)} currently have candidate robots."


def _has_constraint(intent: MissionIntent, key: str) -> bool:
    return any(constraint.key == key and bool(constraint.value) for constraint in intent.constraints)


def _robot_can_support_intent(robot: RobotProfile, intent: MissionIntent) -> bool:
    if robot.status in {"offline", "maintenance"}:
        return False
    if robot.battery_level is not None and robot.battery_level < 20.0:
        return False
    required = set(intent.required_capabilities)
    if not required.issubset(set(robot.capabilities)):
        if intent.mission_type != "cargo_transfer":
            return False
        if not {"cargo_transport"}.issubset(set(robot.capabilities)):
            return False
    return True


def _is_exterior_zone(zone: str | None) -> bool:
    return (zone or "").lower() in {"dock", "landing", "trail"}


def _is_interior_zone(zone: str | None) -> bool:
    return (zone or "").lower() in {"entry", "main-floor", "kitchen"}


def _task_environment(source_zone: str | None, destination_zone: str | None) -> str:
    if _is_exterior_zone(source_zone) and _is_exterior_zone(destination_zone):
        return "outdoor"
    if _is_interior_zone(source_zone) and _is_interior_zone(destination_zone):
        return "indoor"
    return "mixed"


def _zone_connectivity_graph(zone_index: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    graph = {zone_id: set() for zone_id in zone_index}
    for left, right in (
        ("landing", "trail"),
        ("trail", "dock"),
        ("landing", "entry"),
        ("entry", "main-floor"),
        ("main-floor", "kitchen"),
        ("main-floor", "bedroom"),
    ):
        if left in graph and right in graph:
            graph[left].add(right)
            graph[right].add(left)
    return graph


def _find_zone_route(graph: dict[str, set[str]], source: str, destination: str) -> list[str] | None:
    if source == destination:
        return [source]
    if source not in graph or destination not in graph:
        return None
    queue: list[tuple[str, list[str]]] = [(source, [source])]
    visited = {source}
    while queue:
        current, path = queue.pop(0)
        for neighbor in graph.get(current, set()):
            if neighbor in visited:
                continue
            next_path = path + [neighbor]
            if neighbor == destination:
                return next_path
            visited.add(neighbor)
            queue.append((neighbor, next_path))
    return None
