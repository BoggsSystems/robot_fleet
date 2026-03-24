"""
Phase 3 backend services for fleet registry, tasks, commands, and onboarding.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .config import LocalRuntimeConfig
from .persistence import ShadowWorldStore
from .site_graph import load_default_site_graph


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class FleetBackendServices:
    """Service layer for persistent fleet backend entities."""

    store: ShadowWorldStore
    config: LocalRuntimeConfig

    def ensure_defaults(self) -> None:
        now = _utc_now_iso()
        if not any(f["fleet_id"] == self.config.fleet_id for f in self.store.list_fleets()):
            self.store.upsert_fleet(
                {
                    "fleet_id": self.config.fleet_id,
                    "name": "Primary Fleet",
                    "status": "active",
                    "metadata": {"tenant_id": self.config.tenant_id},
                    "created_at": now,
                    "updated_at": now,
                }
            )
        if not any(s["site_id"] == self.config.site_id for s in self.store.list_sites()):
            self.store.upsert_site(
                {
                    "site_id": self.config.site_id,
                    "name": "Local Development Site",
                    "status": "active",
                    "metadata": {"tenant_id": self.config.tenant_id},
                    "created_at": now,
                    "updated_at": now,
                }
            )
        existing_zone_ids = {zone["zone_id"] for zone in self.store.list_zones(site_id=self.config.site_id)}
        for zone_id, name, zone_type in (
            ("landing", "Landing", "handoff"),
            ("trail", "Path", "path"),
            ("dock", "Main Dock", "dock"),
            ("entry", "Entry", "room"),
            ("main-floor", "Main Floor", "room"),
            ("kitchen", "Kitchen", "room"),
        ):
            if zone_id not in existing_zone_ids:
                self.create_zone(zone_id=zone_id, site_id=self.config.site_id, name=name, zone_type=zone_type)
        if len(self.store.list_robot_records(fleet_id=self.config.fleet_id)) == 0:
            self.register_robot(
                robot_id="carrier-01",
                name="Carrier 01",
                ip_address="127.0.0.1",
                network_interface="lo",
                capabilities=["cargo_transport", "rough_terrain", "outdoor", "indoor_delivery"],
                zone_id="dock",
                model="Unitree Go2",
                robot_type="unitree_go2",
                robot_category="Quadruped",
                metadata={"battery_level": 84.0, "payload_capacity_kg": 12.5, "range_minutes": 55},
            )
            self.register_robot(
                robot_id="carrier-02",
                name="Carrier 02",
                ip_address="127.0.0.1",
                network_interface="lo",
                capabilities=["fine_manipulation", "indoor_delivery", "cargo_transport"],
                zone_id="entry",
                model="Unitree G1",
                robot_type="unitree_g1",
                robot_category="Humanoid",
                metadata={"battery_level": 91.0, "payload_capacity_kg": 8.0, "range_minutes": 45},
            )

    def create_fleet(self, fleet_id: str, name: str, status: str = "active", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        now = _utc_now_iso()
        fleet = {
            "fleet_id": fleet_id,
            "name": name,
            "status": status,
            "metadata": metadata or {},
            "created_at": now,
            "updated_at": now,
        }
        self.store.upsert_fleet(fleet)
        return fleet

    def list_fleets(self) -> list[dict[str, Any]]:
        return self.store.list_fleets()

    def create_site(self, site_id: str, name: str, status: str = "active", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        now = _utc_now_iso()
        site = {
            "site_id": site_id,
            "name": name,
            "status": status,
            "metadata": metadata or {},
            "created_at": now,
            "updated_at": now,
        }
        self.store.upsert_site(site)
        return site

    def list_sites(self) -> list[dict[str, Any]]:
        return self.store.list_sites()

    def create_zone(
        self,
        zone_id: str,
        site_id: str,
        name: str,
        zone_type: str = "operational",
        parent_zone_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = _utc_now_iso()
        zone = {
            "zone_id": zone_id,
            "site_id": site_id,
            "name": name,
            "parent_zone_id": parent_zone_id,
            "zone_type": zone_type,
            "metadata": metadata or {},
            "created_at": now,
            "updated_at": now,
        }
        self.store.upsert_zone(zone)
        return zone

    def list_zones(self, site_id: str | None = None) -> list[dict[str, Any]]:
        return self.store.list_zones(site_id=site_id)

    def get_site_graph(self):
        return load_default_site_graph()

    def register_robot(
        self,
        *,
        robot_id: str,
        name: str,
        ip_address: str,
        network_interface: str,
        capabilities: list[str],
        zone_id: str | None = None,
        fleet_id: str | None = None,
        site_id: str | None = None,
        model: str = "Unitree R1",
        serial: str = "",
        firmware: str = "",
        robot_type: str = "unitree_r1",
        robot_category: str = "Humanoid",
        vendor: str = "unitree_sdk2",
        status: str = "idle",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = _utc_now_iso()
        robot = {
            "robot_id": robot_id,
            "fleet_id": fleet_id or self.config.fleet_id,
            "site_id": site_id or self.config.site_id,
            "zone_id": zone_id,
            "name": name,
            "status": status,
            "ip_address": ip_address,
            "network_interface": network_interface,
            "model": model,
            "serial": serial,
            "firmware": firmware,
            "robot_type": robot_type,
            "robot_category": robot_category,
            "vendor": vendor,
            "capabilities": capabilities,
            "metadata": metadata or {},
            "created_at": now,
            "updated_at": now,
        }
        self.store.upsert_robot_record(robot)
        self.store.upsert_onboarding_record(
            {
                "robot_id": robot_id,
                "stage": "registered",
                "status": "completed",
                "details": {"ip_address": ip_address, "zone_id": zone_id},
                "updated_at": now,
            }
        )
        return robot

    def get_robot(self, robot_id: str) -> dict[str, Any] | None:
        return self.store.get_robot_record(robot_id)

    def list_robots(self, fleet_id: str | None = None) -> list[dict[str, Any]]:
        return self.store.list_robot_records(fleet_id=fleet_id)

    def update_robot_status(self, robot_id: str, status: str, zone_id: str | None = None) -> dict[str, Any]:
        return self.store.update_robot_record_status(robot_id, status, zone_id=zone_id)

    def update_robot_profile(
        self,
        robot_id: str,
        *,
        status: str | None = None,
        zone_id: str | None = None,
        capabilities: list[str] | None = None,
        metadata_updates: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        robot = self.store.get_robot_record(robot_id)
        if robot is None:
            raise ValueError(f"Robot {robot_id} not found")
        if status is not None:
            robot["status"] = status
        if zone_id is not None:
            robot["zone_id"] = zone_id
        if capabilities is not None:
            robot["capabilities"] = capabilities
        if metadata_updates:
            merged = dict(robot.get("metadata", {}))
            merged.update(metadata_updates)
            robot["metadata"] = merged
        robot["updated_at"] = _utc_now_iso()
        self.store.upsert_robot_record(robot)
        return robot

    def create_task(
        self,
        *,
        task_type: str,
        spec: dict[str, Any],
        fleet_id: str | None = None,
        site_id: str | None = None,
        robot_id: str | None = None,
        zone_id: str | None = None,
    ) -> dict[str, Any]:
        now = _utc_now_iso()
        task = {
            "task_id": f"task-{uuid4()}",
            "robot_id": robot_id,
            "fleet_id": fleet_id or self.config.fleet_id,
            "site_id": site_id or self.config.site_id,
            "zone_id": zone_id,
            "task_type": task_type,
            "status": "queued",
            "spec": spec,
            "result": {},
            "created_at": now,
            "updated_at": now,
        }
        self.store.upsert_task_record(task)
        return task

    def update_task_status(self, task_id: str, status: str, result: dict[str, Any] | None = None) -> dict[str, Any]:
        current = self.store.get_task_record(task_id)
        if current is None:
            raise ValueError(f"Task {task_id} not found")
        prior_status = current.get("status")
        robot_id = current.get("robot_id")
        current["status"] = status
        if result is not None:
            current["result"] = result
        current["updated_at"] = _utc_now_iso()
        self.store.upsert_task_record(current)
        if robot_id and status in {"completed", "failed"} and prior_status not in {"completed", "failed"}:
            self.update_robot_status(robot_id, "idle")
        return current

    def assign_task(self, task_id: str, robot_id: str) -> dict[str, Any]:
        task = self.store.get_task_record(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        robot = self.store.get_robot_record(robot_id)
        if robot is None:
            raise ValueError(f"Robot {robot_id} not found")
        task["robot_id"] = robot_id
        task["status"] = "assigned"
        task["updated_at"] = _utc_now_iso()
        self.store.upsert_task_record(task)
        self.update_robot_status(robot_id, "busy", zone_id=task.get("zone_id"))
        return task

    def list_tasks(self, status: str | None = None) -> list[dict[str, Any]]:
        return self.store.list_task_records(status=status)

    def activate_ready_tasks(self) -> list[dict[str, Any]]:
        paused_missions = {
            session["mission_id"]
            for session in self.store.list_mission_sessions(limit=200)
            if session["status"] in {"paused", "cancelled", "clarification_required"}
        }
        tasks = self.store.list_task_records()
        indexed = {task["task_id"]: task for task in tasks}
        activated: list[dict[str, Any]] = []

        for task in tasks:
            if task.get("status") != "queued":
                continue
            spec = dict(task.get("spec") or {})
            if spec.get("mission_id") in paused_missions:
                continue
            depends_on = [dependency for dependency in spec.get("depends_on", []) if dependency]
            if depends_on and not all(indexed.get(dependency, {}).get("status") == "completed" for dependency in depends_on):
                continue

            planned_robot_id = spec.get("planned_robot_id")
            if not planned_robot_id:
                continue

            robot = self.store.get_robot_record(planned_robot_id)
            if robot is None:
                continue
            if robot.get("status") not in {"idle", "available_soon"}:
                continue

            activated.append(self.assign_task(task["task_id"], planned_robot_id))

        return activated

    def set_task_status(self, task_id: str, status: str, result: dict[str, Any] | None = None) -> dict[str, Any]:
        task = self.store.get_task_record(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        if status == "queued":
            if task.get("robot_id"):
                self.update_robot_status(task["robot_id"], "idle")
            task["robot_id"] = None
            task["status"] = "queued"
            if result is not None:
                task["result"] = result
            task["updated_at"] = _utc_now_iso()
            self.store.upsert_task_record(task)
            return task
        return self.update_task_status(task_id, status, result=result)

    def pause_mission(self, mission_id: str, *, requested_by: str) -> dict[str, Any]:
        session = self.store.get_mission_session(mission_id)
        if session is None:
            raise ValueError(f"Mission {mission_id} not found")

        for task_id in session.get("task_ids", []):
            task = self.store.get_task_record(task_id)
            if task is None:
                continue
            if task["status"] in {"assigned", "running"}:
                self.set_task_status(task_id, "queued")

        metadata = self._append_mission_event(
            session.get("metadata", {}),
            message=f"Mission paused by {requested_by}.",
            tone="warn",
            status="paused",
        )
        return self.upsert_mission_session(
            mission_id=mission_id,
            request_text=session["request_text"],
            requested_by=session["requested_by"],
            status="paused",
            preview=session.get("preview", {}),
            question=session.get("question", {}),
            task_ids=session.get("task_ids", []),
            metadata=metadata,
            created_at=session["created_at"],
        )

    def resume_mission(self, mission_id: str, *, requested_by: str) -> dict[str, Any]:
        session = self.store.get_mission_session(mission_id)
        if session is None:
            raise ValueError(f"Mission {mission_id} not found")

        metadata = self._append_mission_event(
            session.get("metadata", {}),
            message=f"Mission resumed by {requested_by}.",
            tone="live",
            status="in_progress",
        )
        updated = self.upsert_mission_session(
            mission_id=mission_id,
            request_text=session["request_text"],
            requested_by=session["requested_by"],
            status="in_progress",
            preview=session.get("preview", {}),
            question=session.get("question", {}),
            task_ids=session.get("task_ids", []),
            metadata=metadata,
            created_at=session["created_at"],
        )
        self.refresh_mission_sessions()
        return self.store.get_mission_session(mission_id) or updated

    def retry_mission(self, mission_id: str, *, requested_by: str) -> dict[str, Any]:
        session = self.store.get_mission_session(mission_id)
        if session is None:
            raise ValueError(f"Mission {mission_id} not found")

        for task_id in session.get("task_ids", []):
            task = self.store.get_task_record(task_id)
            if task is None:
                continue
            if task["status"] == "failed":
                self.set_task_status(task_id, "queued", result={})

        metadata = self._append_mission_event(
            session.get("metadata", {}),
            message=f"Mission retry requested by {requested_by}.",
            tone="live",
            status="in_progress",
        )
        updated = self.upsert_mission_session(
            mission_id=mission_id,
            request_text=session["request_text"],
            requested_by=session["requested_by"],
            status="in_progress",
            preview=session.get("preview", {}),
            question=session.get("question", {}),
            task_ids=session.get("task_ids", []),
            metadata=metadata,
            created_at=session["created_at"],
        )
        self.refresh_mission_sessions()
        return self.store.get_mission_session(mission_id) or updated

    def propose_mission_replan(self, mission_id: str, *, requested_by: str) -> dict[str, Any]:
        session = self.store.get_mission_session(mission_id)
        if session is None:
            raise ValueError(f"Mission {mission_id} not found")
        if session["status"] not in {"blocked", "in_progress", "approved", "dispatched"}:
            raise ValueError(f"Mission {mission_id} is {session['status']} and cannot be replanned")

        tasks = [
            self.store.get_task_record(task_id)
            for task_id in session.get("task_ids", [])
        ]
        tasks = [task for task in tasks if task is not None]
        tasks.sort(key=lambda task: (task.get("spec") or {}).get("step_index", 999))
        if not tasks:
            raise ValueError(f"Mission {mission_id} has no dispatched tasks to replan")

        candidate = next((task for task in tasks if task["status"] == "failed"), None)
        if candidate is None:
            candidate = next((task for task in tasks if task["status"] in {"queued", "assigned", "running"}), None)
        if candidate is None:
            raise ValueError(f"Mission {mission_id} has no active or blocked task to replan")

        fallback_robot_ids = self.available_fallback_robot_ids(candidate["task_id"])
        spec = dict(candidate.get("spec") or {})
        blocked_reason = (
            (candidate.get("result") or {}).get("reason")
            or dict(spec.get("context") or {}).get("failure_reason")
            or "Task requires operator review."
        )
        route_override = self._proposed_route_override(candidate, blocked_reason)

        if route_override:
            action = "reroute"
            summary = (
                f"Reroute {spec.get('summary') or candidate['task_type']} via "
                f"{' -> '.join(zone.title() for zone in route_override)}."
            )
            warnings = ["Route override is based on the local site graph and should be reviewed before execution."]
        elif fallback_robot_ids:
            action = "use_fallback"
            summary = f"Reassign {spec.get('summary') or candidate['task_type']} to the best available fallback robot."
            warnings = []
        elif candidate["status"] == "failed":
            action = "retry"
            summary = f"Retry {spec.get('summary') or candidate['task_type']} with the existing mission plan."
            warnings = ["No allocatable fallback robot is currently available, so the mission will retry the blocked step."]
        else:
            action = "pause"
            summary = f"Pause the mission while the blocked condition is reviewed."
            warnings = ["No reassignable step was found, so the safest action is to pause the mission."]

        replan = {
            "missionId": mission_id,
            "status": "candidate",
            "action": action,
            "summary": summary,
            "reason": blocked_reason,
            "taskId": candidate["task_id"],
            "taskSummary": spec.get("summary") or candidate.get("task_type"),
            "candidateRobotIds": fallback_robot_ids,
            "routeNodes": route_override or [],
            "routeLabels": self.get_site_graph().route_labels(route_override),
            "warnings": warnings,
            "reviewSummary": _local_replan_review_summary(action, blocked_reason, route_override),
            "operatorNotes": _local_replan_operator_notes(action, spec, route_override),
            "provider": "local-replan",
            "generatedAt": _utc_now_iso(),
            "requestedBy": requested_by,
        }
        replan = self._maybe_enrich_replan(replan, session=session, task=candidate)

        metadata = dict(session.get("metadata", {}))
        metadata["pending_replan"] = replan
        metadata = self._append_mission_event(
            metadata,
            message=f"Replan proposed by {requested_by}: {summary}",
            tone="warn",
            status="replan_pending",
            task_id=candidate["task_id"],
        )
        return self.upsert_mission_session(
            mission_id=mission_id,
            request_text=session["request_text"],
            requested_by=session["requested_by"],
            status=session["status"],
            preview=session.get("preview", {}),
            question=session.get("question", {}),
            request_payload=session.get("request", {}),
            proposal=session.get("proposal", {}),
            validated_plan=session.get("validated_plan", {}),
            approval=session.get("approval", {}),
            task_ids=session.get("task_ids", []),
            metadata=metadata,
            created_at=session["created_at"],
        )

    def apply_mission_replan(self, mission_id: str, *, requested_by: str) -> dict[str, Any]:
        session = self.store.get_mission_session(mission_id)
        if session is None:
            raise ValueError(f"Mission {mission_id} not found")

        metadata = dict(session.get("metadata", {}))
        replan = dict(metadata.get("pending_replan") or {})
        if not replan:
            raise ValueError(f"Mission {mission_id} has no pending replan proposal")

        action = replan.get("action")
        if action == "use_fallback":
            task_id = replan.get("taskId")
            candidate_robot_ids = list(replan.get("candidateRobotIds", []))
            if not task_id or not candidate_robot_ids:
                raise ValueError(f"Mission {mission_id} replan has no fallback candidate")
            self.reassign_task_to_robot(task_id, candidate_robot_ids[0], consume_fallback=True)
            updated_status = "in_progress"
        elif action == "reroute":
            task_id = replan.get("taskId")
            route_nodes = list(replan.get("routeNodes", []))
            if not task_id or len(route_nodes) < 2:
                raise ValueError(f"Mission {mission_id} replan has no valid route override")
            self.apply_task_route_override(task_id, route_nodes)
            updated_status = "in_progress"
        elif action == "retry":
            updated = self.retry_mission(mission_id, requested_by=requested_by)
            metadata = dict(updated.get("metadata", {}))
            metadata.pop("pending_replan", None)
            metadata = self._append_mission_event(
                metadata,
                message=f"Replan applied by {requested_by}: retry mission.",
                tone="live",
                status="replan_applied",
                task_id=replan.get("taskId"),
            )
            return self.upsert_mission_session(
                mission_id=mission_id,
                request_text=updated["request_text"],
                requested_by=updated["requested_by"],
                status=updated["status"],
                preview=updated.get("preview", {}),
                question=updated.get("question", {}),
                request_payload=updated.get("request", {}),
                proposal=updated.get("proposal", {}),
                validated_plan=updated.get("validated_plan", {}),
                approval=updated.get("approval", {}),
                task_ids=updated.get("task_ids", []),
                metadata=metadata,
                created_at=updated["created_at"],
            )
        elif action == "pause":
            updated = self.pause_mission(mission_id, requested_by=requested_by)
            metadata = dict(updated.get("metadata", {}))
            metadata.pop("pending_replan", None)
            metadata = self._append_mission_event(
                metadata,
                message=f"Replan applied by {requested_by}: pause mission.",
                tone="warn",
                status="replan_applied",
                task_id=replan.get("taskId"),
            )
            return self.upsert_mission_session(
                mission_id=mission_id,
                request_text=updated["request_text"],
                requested_by=updated["requested_by"],
                status=updated["status"],
                preview=updated.get("preview", {}),
                question=updated.get("question", {}),
                request_payload=updated.get("request", {}),
                proposal=updated.get("proposal", {}),
                validated_plan=updated.get("validated_plan", {}),
                approval=updated.get("approval", {}),
                task_ids=updated.get("task_ids", []),
                metadata=metadata,
                created_at=updated["created_at"],
            )
        else:
            raise ValueError(f"Mission {mission_id} has unsupported replan action '{action}'")

        metadata.pop("pending_replan", None)
        metadata = self._append_mission_event(
            metadata,
            message=f"Replan applied by {requested_by}: {replan.get('summary') or action}.",
            tone="live",
            status="replan_applied",
            task_id=replan.get("taskId"),
        )
        updated = self.upsert_mission_session(
            mission_id=mission_id,
            request_text=session["request_text"],
            requested_by=session["requested_by"],
            status=updated_status,
            preview=session.get("preview", {}),
            question=session.get("question", {}),
            request_payload=session.get("request", {}),
            proposal=session.get("proposal", {}),
            validated_plan=session.get("validated_plan", {}),
            approval=session.get("approval", {}),
            task_ids=session.get("task_ids", []),
            metadata=metadata,
            created_at=session["created_at"],
        )
        self.refresh_mission_sessions()
        return self.store.get_mission_session(mission_id) or updated

    def use_mission_fallback(self, mission_id: str, *, requested_by: str) -> dict[str, Any]:
        session = self.store.get_mission_session(mission_id)
        if session is None:
            raise ValueError(f"Mission {mission_id} not found")

        tasks = [
            self.store.get_task_record(task_id)
            for task_id in session.get("task_ids", [])
        ]
        tasks = [task for task in tasks if task is not None]
        tasks.sort(key=lambda task: (task.get("spec") or {}).get("step_index", 999))

        candidate = next(
            (
                task
                for task in tasks
                if task["status"] in {"failed", "queued", "assigned", "running"}
                and (task.get("spec") or {}).get("fallback_robot_ids")
            ),
            None,
        )
        if candidate is None:
            raise ValueError(f"Mission {mission_id} has no task with configured fallback robots")

        reassigned = self.reassign_task_to_fallback(candidate["task_id"])
        metadata = self._append_mission_event(
            session.get("metadata", {}),
            message=f"Fallback reassignment requested by {requested_by} for {(candidate.get('spec') or {}).get('summary') or candidate['task_type']}.",
            tone="warn",
            status="fallback_assigned",
            task_id=candidate["task_id"],
        )
        updated = self.upsert_mission_session(
            mission_id=mission_id,
            request_text=session["request_text"],
            requested_by=session["requested_by"],
            status="in_progress",
            preview=session.get("preview", {}),
            question=session.get("question", {}),
            task_ids=session.get("task_ids", []),
            metadata=metadata,
            created_at=session["created_at"],
        )
        self.refresh_mission_sessions()
        return self.store.get_mission_session(mission_id) or updated

    def reassign_task_to_fallback(self, task_id: str) -> dict[str, Any]:
        task = self.store.get_task_record(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        spec = dict(task.get("spec") or {})
        fallback_robot_ids = self.available_fallback_robot_ids(task_id)

        selected_robot_id = None
        for robot_id in fallback_robot_ids:
            robot = self.store.get_robot_record(robot_id)
            if robot is None:
                continue
            if robot.get("status") in {"idle", "available_soon"}:
                selected_robot_id = robot_id
                break
        if selected_robot_id is None:
            raise ValueError(f"Task {task_id} has no available fallback robot")

        return self.reassign_task_to_robot(task_id, selected_robot_id, consume_fallback=True)

    def reassign_task_to_robot(self, task_id: str, robot_id: str, *, consume_fallback: bool = False) -> dict[str, Any]:
        task = self.store.get_task_record(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        spec = dict(task.get("spec") or {})
        if task.get("robot_id"):
            self.update_robot_status(task["robot_id"], "idle")

        spec["planned_robot_id"] = robot_id
        context = dict(spec.get("context", {}))
        context["fallback_reassigned"] = True
        context["failure_reason"] = ""
        spec["context"] = context
        if consume_fallback:
            fallback_robot_ids = [candidate for candidate in self.available_fallback_robot_ids(task_id) if candidate != robot_id]
            spec["fallback_robot_ids"] = fallback_robot_ids
        task["spec"] = spec
        task["robot_id"] = None
        task["status"] = "queued"
        task["result"] = {}
        task["updated_at"] = _utc_now_iso()
        self.store.upsert_task_record(task)
        return self.assign_task(task_id, robot_id)

    def apply_task_route_override(self, task_id: str, route_nodes: list[str]) -> dict[str, Any]:
        task = self.store.get_task_record(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        spec = dict(task.get("spec") or {})
        context = dict(spec.get("context", {}))
        context["route_replanned"] = True
        context["failure_reason"] = ""
        spec["context"] = context
        spec["route_override"] = route_nodes
        spec["route"] = " -> ".join(route_nodes)
        if route_nodes:
            spec["source_zone"] = route_nodes[0]
            spec["destination_zone"] = route_nodes[-1]
            task["zone_id"] = route_nodes[0]
        task["spec"] = spec
        task["result"] = {}
        current_robot_id = task.get("robot_id")
        if current_robot_id:
            self.update_robot_status(current_robot_id, "idle")
        task["robot_id"] = None
        task["status"] = "queued"
        task["updated_at"] = _utc_now_iso()
        self.store.upsert_task_record(task)
        planned_robot_id = spec.get("planned_robot_id")
        if planned_robot_id:
            robot = self.store.get_robot_record(planned_robot_id)
            if robot and robot.get("status") in {"idle", "available_soon"}:
                return self.assign_task(task_id, planned_robot_id)
        return task

    def get_pending_replan(self, mission_id: str) -> dict[str, Any] | None:
        session = self.store.get_mission_session(mission_id)
        if session is None:
            return None
        return dict(session.get("metadata", {}).get("pending_replan") or {}) or None

    def _maybe_enrich_replan(self, replan: dict[str, Any], *, session: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
        try:
            from .brain.openai_replan import OpenAIReplanService
        except Exception:
            return replan

        service = OpenAIReplanService()
        context = {
            "request_text": session.get("request_text"),
            "mission_status": session.get("status"),
            "task": {
                "task_id": task.get("task_id"),
                "task_type": task.get("task_type"),
                "summary": (task.get("spec") or {}).get("summary"),
                "route": (task.get("spec") or {}).get("route"),
                "step_index": (task.get("spec") or {}).get("step_index"),
            },
            "site_graph_path": str(self.get_site_graph().source_path),
        }
        return service.enrich(replan, context)

    def _proposed_route_override(self, task: dict[str, Any], blocked_reason: str) -> list[str] | None:
        spec = dict(task.get("spec") or {})
        source_zone = str(spec.get("source_zone") or task.get("zone_id") or "").lower()
        destination_zone = str(spec.get("destination_zone") or "").lower()
        if not source_zone or not destination_zone:
            return None

        blocked_zone = _infer_blocked_zone(blocked_reason)
        if not blocked_zone:
            return None

        route = self.get_site_graph().route_between(source_zone, destination_zone, blocked_node=blocked_zone)
        if route is None:
            return None
        return route

    def available_fallback_robot_ids(self, task_id: str) -> list[str]:
        task = self.store.get_task_record(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        spec = dict(task.get("spec") or {})
        fallback_robot_ids = [robot_id for robot_id in spec.get("fallback_robot_ids", []) if robot_id]
        if fallback_robot_ids:
            return fallback_robot_ids
        return _candidate_robot_ids_for_task(self.store.list_robot_records(fleet_id=self.config.fleet_id), task)

    def create_command(
        self,
        *,
        robot_id: str,
        command_type: str,
        parameters: dict[str, Any],
        issued_by: str,
    ) -> dict[str, Any]:
        now = _utc_now_iso()
        command = {
            "command_id": f"cmd-{uuid4()}",
            "robot_id": robot_id,
            "command_type": command_type,
            "status": "queued",
            "parameters": parameters,
            "issued_by": issued_by,
            "created_at": now,
            "updated_at": now,
        }
        self.store.upsert_command_record(command)
        return command

    def update_command_status(self, command_id: str, status: str) -> dict[str, Any]:
        current = self.store.get_command_record(command_id)
        if current is None:
            raise ValueError(f"Command {command_id} not found")
        current["status"] = status
        current["updated_at"] = _utc_now_iso()
        self.store.upsert_command_record(current)
        return current

    def list_commands(self, robot_id: str | None = None) -> list[dict[str, Any]]:
        return self.store.list_command_records(robot_id=robot_id)

    def get_onboarding(self, robot_id: str) -> dict[str, Any] | None:
        return self.store.get_onboarding_record(robot_id)

    def update_onboarding(
        self,
        robot_id: str,
        *,
        stage: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if self.store.get_robot_record(robot_id) is None:
            raise ValueError(f"Robot {robot_id} not found")
        record = {
            "robot_id": robot_id,
            "stage": stage,
            "status": status,
            "details": details or {},
            "updated_at": _utc_now_iso(),
        }
        self.store.upsert_onboarding_record(record)
        return record

    def record_calibration_step(self, robot_id: str, step: str, success: bool, message: str) -> dict[str, Any]:
        onboarding = self.get_onboarding(robot_id) or {
            "robot_id": robot_id,
            "stage": "registered",
            "status": "pending",
            "details": {},
        }
        details = dict(onboarding.get("details", {}))
        completed_steps = details.setdefault("calibration_steps", {})
        completed_steps[step] = {
            "success": success,
            "message": message,
            "updated_at": _utc_now_iso(),
        }
        stage = "calibration" if step != "movement" else "ready_for_operations"
        status = "completed" if success and step == "movement" else ("in_progress" if success else "failed")
        return self.update_onboarding(robot_id, stage=stage, status=status, details=details)

    def execute_robot_command(self, robot_id: str, command_type: str, parameters: dict[str, Any], controller: Any | None = None) -> dict[str, Any]:
        if controller is None:
            return {"success": False, "error": "No controller available"}
        robot = controller.get_robot(robot_id)
        if robot is None:
            raise ValueError(f"Robot {robot_id} not connected to controller")

        if command_type == "stand_up":
            ok = robot.stand_up()
            return {"success": ok, "action": "stand_up"}
        if command_type == "recovery_stand":
            ok = robot.recovery_stand()
            return {"success": ok, "action": "recovery_stand"}
        if command_type == "walk_forward":
            meters = float(parameters.get("meters", 0.0))
            ok = robot.walk_forward(meters)
            return {"success": ok, "action": "walk_forward", "meters": meters}
        if command_type == "turn":
            degrees = float(parameters.get("degrees", 0.0))
            ok = robot.turn(degrees)
            return {"success": ok, "action": "turn", "degrees": degrees}
        if command_type == "perform_action":
            action_name = str(parameters.get("action_name", "")).strip()
            if not action_name:
                return {"success": False, "error": "perform_action requires action_name"}
            ok = robot.perform_action(action_name)
            return {"success": ok, "action": "perform_action", "action_name": action_name}

        return {"success": False, "error": f"Unsupported command_type: {command_type}"}

    def execute_task(self, task_id: str, controller: Any | None = None) -> dict[str, Any]:
        task = self.store.get_task_record(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        if not task.get("robot_id"):
            raise ValueError(f"Task {task_id} has no assigned robot")

        robot_id = task["robot_id"]
        self.update_task_status(task_id, "running")
        self.update_robot_status(robot_id, "busy", zone_id=task.get("zone_id"))

        if controller is None:
            return self.update_task_status(task_id, "running")

        from .pilot_module import run_single_task

        task_spec = self._runtime_task_spec(task)
        controller.assign_task(task_id, robot_id, task_spec)
        result = run_single_task(controller, robot_id, task_id, task_spec)
        final_status = "completed" if result.get("success") else "failed"
        updated = self.update_task_status(task_id, final_status, result=result)
        self.update_robot_status(robot_id, "idle")
        return updated

    def _runtime_task_spec(self, task: dict[str, Any]) -> dict[str, Any]:
        spec = dict(task.get("spec") or {})
        return {
            "type": task["task_type"],
            "params": {
                **spec,
                "task_id": task["task_id"],
                "source_zone": spec.get("source_zone") or task.get("zone_id"),
                "destination_zone": spec.get("destination_zone"),
            },
        }

    def dispatch_command(self, command_id: str, controller: Any | None = None) -> dict[str, Any]:
        command = self.store.get_command_record(command_id)
        if command is None:
            raise ValueError(f"Command {command_id} not found")

        command = self.update_command_status(command_id, "dispatched")

        if controller is None:
            return command

        if command["command_type"] == "start_task":
            task_id = command["parameters"].get("task_id")
            if not task_id:
                raise ValueError("start_task command requires task_id")
            self.execute_task(task_id, controller=controller)
            return self.update_command_status(command_id, "completed")
        result = self.execute_robot_command(
            command["robot_id"],
            command["command_type"],
            command["parameters"],
            controller=controller,
        )
        if result.get("success"):
            return self.update_command_status(command_id, "completed")
        return self.update_command_status(command_id, "failed")

    def fleet_overview(self) -> dict[str, Any]:
        return {
            "fleets": self.list_fleets(),
            "sites": self.list_sites(),
            "zones": self.list_zones(),
            "robots": self.list_robots(),
            "tasks": self.list_tasks(),
            "commands": self.list_commands(),
            "missions": self.list_mission_sessions(),
        }

    def upsert_mission_session(
        self,
        *,
        mission_id: str,
        request_text: str,
        requested_by: str,
        status: str,
        preview: dict[str, Any] | None = None,
        question: dict[str, Any] | None = None,
        request_payload: dict[str, Any] | None = None,
        proposal: dict[str, Any] | None = None,
        validated_plan: dict[str, Any] | None = None,
        approval: dict[str, Any] | None = None,
        task_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        created_at: str | None = None,
    ) -> dict[str, Any]:
        now = _utc_now_iso()
        current = self.store.get_mission_session(mission_id)
        session = {
            "mission_id": mission_id,
            "request_text": request_text,
            "requested_by": requested_by,
            "status": status,
            "preview": preview if preview is not None else (current.get("preview", {}) if current else {}),
            "question": question if question is not None else (current.get("question", {}) if current else {}),
            "request": request_payload if request_payload is not None else (current.get("request", {}) if current else {}),
            "proposal": proposal if proposal is not None else (current.get("proposal", {}) if current else {}),
            "validated_plan": validated_plan if validated_plan is not None else (current.get("validated_plan", {}) if current else {}),
            "approval": approval if approval is not None else (current.get("approval", {}) if current else {}),
            "task_ids": task_ids if task_ids is not None else (current.get("task_ids", []) if current else []),
            "metadata": metadata if metadata is not None else (current.get("metadata", {}) if current else {}),
            "created_at": created_at or (current.get("created_at") if current else now),
            "updated_at": now,
        }
        self.store.upsert_mission_session(session)
        return session

    def get_mission_session(self, mission_id: str) -> dict[str, Any] | None:
        return self.store.get_mission_session(mission_id)

    def list_mission_sessions(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.store.list_mission_sessions(limit=limit)

    def refresh_mission_sessions(self, limit: int = 50) -> list[dict[str, Any]]:
        self.activate_ready_tasks()
        sessions = self.store.list_mission_sessions(limit=limit)
        return [self._refresh_mission_session(session) for session in sessions]

    def _refresh_mission_session(self, session: dict[str, Any]) -> dict[str, Any]:
        if session["status"] in {"clarification_required", "cancelled"}:
            return session

        task_records = [
            self.store.get_task_record(task_id)
            for task_id in session.get("task_ids", [])
        ]
        task_records = [task for task in task_records if task is not None]
        if not task_records:
            return session

        ordered_tasks = sorted(
            task_records,
            key=lambda task: (task.get("spec") or {}).get("step_index", 999),
        )
        task_statuses = {task["task_id"]: task["status"] for task in ordered_tasks}
        completed_task_ids = [task["task_id"] for task in ordered_tasks if task["status"] == "completed"]
        blocked_task_ids = [task["task_id"] for task in ordered_tasks if task["status"] == "failed"]
        active_task = next(
            (
                task
                for task in ordered_tasks
                if task["status"] in {"assigned", "running", "queued"}
            ),
            None,
        )
        active_task_id = active_task["task_id"] if active_task else None

        if session["status"] == "paused":
            current_status = "paused"
        elif blocked_task_ids:
            current_status = "blocked"
        elif ordered_tasks and len(completed_task_ids) == len(ordered_tasks):
            current_status = "completed"
        elif any(task["status"] in {"assigned", "running", "queued"} for task in ordered_tasks):
            current_status = "in_progress"
        else:
            current_status = session["status"]

        metadata = dict(session.get("metadata", {}))
        previous_statuses = dict(metadata.get("task_statuses", {}))
        previous_mission_status = metadata.get("mission_runtime_status", session["status"])
        timeline = list(metadata.get("mission_events", []))

        for task in ordered_tasks:
            previous = previous_statuses.get(task["task_id"])
            current = task["status"]
            if previous == current:
                continue
            timeline.append(
                {
                    "id": f"msn-evt-{uuid4().hex[:10]}",
                    "time": _utc_now_iso(),
                    "task_id": task["task_id"],
                    "status": current,
                    "tone": _event_tone_for_status(current),
                    "message": _task_event_message(task, current),
                }
            )

        if previous_mission_status != current_status:
            timeline.append(
                {
                    "id": f"msn-evt-{uuid4().hex[:10]}",
                    "time": _utc_now_iso(),
                    "status": current_status,
                    "tone": _event_tone_for_status(current_status),
                    "message": _mission_event_message(session["request_text"], current_status),
                }
            )

        updated_metadata = {
            **metadata,
            "mission_runtime_status": current_status,
            "task_statuses": task_statuses,
            "active_task_id": active_task_id,
            "completed_task_ids": completed_task_ids,
            "blocked_task_ids": blocked_task_ids,
            "mission_events": timeline[-25:],
        }

        if (
            current_status == session["status"]
            and updated_metadata == metadata
        ):
            return session

        return self.upsert_mission_session(
            mission_id=session["mission_id"],
            request_text=session["request_text"],
            requested_by=session["requested_by"],
            status=current_status,
            preview=session.get("preview", {}),
            question=session.get("question", {}),
            request_payload=session.get("request", {}),
            proposal=session.get("proposal", {}),
            validated_plan=session.get("validated_plan", {}),
            approval=session.get("approval", {}),
            task_ids=session.get("task_ids", []),
            metadata=updated_metadata,
            created_at=session["created_at"],
        )

    def _append_mission_event(
        self,
        metadata: dict[str, Any],
        *,
        message: str,
        tone: str,
        status: str,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        updated = dict(metadata or {})
        timeline = list(updated.get("mission_events", []))
        timeline.append(
            {
                "id": f"msn-evt-{uuid4().hex[:10]}",
                "time": _utc_now_iso(),
                "task_id": task_id,
                "status": status,
                "tone": tone,
                "message": message,
            }
        )
        updated["mission_events"] = timeline[-25:]
        return updated


def _event_tone_for_status(status: str) -> str:
    if status in {"failed", "blocked"}:
        return "warn"
    if status in {"completed"}:
        return "ok"
    return "live"


def _task_event_message(task: dict[str, Any], status: str) -> str:
    summary = (task.get("spec") or {}).get("summary") or task.get("task_type", "Task")
    if status == "assigned":
        return f"{summary} assigned to {task.get('robot_id') or 'planned robot'}."
    if status == "running":
        return f"{summary} is running."
    if status == "completed":
        return f"{summary} completed."
    if status == "failed":
        return f"{summary} failed and requires intervention."
    return f"{summary} is {status}."


def _mission_event_message(request_text: str, status: str) -> str:
    if status == "completed":
        return f"Mission completed: {request_text}"
    if status == "blocked":
        return f"Mission blocked: {request_text}"
    if status == "in_progress":
        return f"Mission in progress: {request_text}"
    return f"Mission status changed to {status}: {request_text}"


def _candidate_robot_ids_for_task(robots: list[dict[str, Any]], task: dict[str, Any]) -> list[str]:
    spec = dict(task.get("spec") or {})
    required_capabilities = set(spec.get("required_capabilities", []))
    preferred_robot_types = {value.lower() for value in spec.get("preferred_robot_types", []) if isinstance(value, str)}
    minimum_battery_level = spec.get("minimum_battery_level")
    payload_weight_kg = spec.get("payload_weight_kg")
    current_robot_id = task.get("robot_id")
    planned_robot_id = spec.get("planned_robot_id")

    candidates: list[tuple[float, str]] = []
    for robot in robots:
        robot_id = robot["robot_id"]
        if robot_id in {current_robot_id, planned_robot_id}:
            continue
        if robot.get("status") not in {"idle", "available_soon"}:
            continue

        robot_capabilities = set(robot.get("capabilities", []))
        if not required_capabilities.issubset(robot_capabilities):
            continue

        metadata = dict(robot.get("metadata", {}))
        battery_level = metadata.get("battery_level")
        if minimum_battery_level is not None and battery_level is not None and float(battery_level) < float(minimum_battery_level):
            continue

        payload_capacity = metadata.get("payload_capacity_kg")
        if payload_weight_kg is not None and payload_capacity is not None and float(payload_capacity) < float(payload_weight_kg):
            continue

        score = float(battery_level or 0.0) / 100.0
        robot_type = f"{robot.get('robot_category', '')} {robot.get('robot_type', '')}".lower()
        if preferred_robot_types and any(preferred in robot_type for preferred in preferred_robot_types):
            score += 0.5
        score += min(len(required_capabilities & robot_capabilities) * 0.1, 0.3)
        candidates.append((score, robot_id))

    candidates.sort(reverse=True)
    return [robot_id for _, robot_id in candidates]


def _zone_connectivity_graph(zones: list[dict[str, Any]]) -> dict[str, set[str]]:
    graph = {
        str(zone.get("zone_id") or "").lower(): set()
        for zone in zones
        if zone.get("zone_id")
    }
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


def _find_zone_route(
    graph: dict[str, set[str]],
    source: str,
    destination: str,
    *,
    blocked_zone: str | None = None,
) -> list[str] | None:
    if source == destination:
        return [source]
    if source not in graph or destination not in graph:
        return None
    blocked = blocked_zone.lower() if blocked_zone else None
    if blocked in {source, destination}:
        return None

    queue: list[tuple[str, list[str]]] = [(source, [source])]
    visited = {source}
    while queue:
        current, path = queue.pop(0)
        for neighbor in graph.get(current, set()):
            if neighbor == blocked or neighbor in visited:
                continue
            next_path = path + [neighbor]
            if neighbor == destination:
                return next_path
            visited.add(neighbor)
            queue.append((neighbor, next_path))
    return None


def _infer_blocked_zone(reason: str | None) -> str | None:
    normalized = str(reason or "").lower()
    for zone in ("main-floor", "kitchen", "entry", "dock", "landing", "trail", "path"):
        if zone in normalized:
            return "trail" if zone == "path" else zone
    return None


def _local_replan_review_summary(action: str, reason: str, route_override: list[str] | None) -> str:
    if action == "reroute" and route_override:
        return f"Route issue detected: {reason}. Proposed reroute keeps the mission moving without changing the assigned task type."
    if action == "use_fallback":
        return f"Execution issue detected: {reason}. Proposed fallback keeps the current mission structure and swaps execution to another robot."
    if action == "retry":
        return f"Execution issue detected: {reason}. Proposed retry keeps the existing plan and attempts the blocked step again."
    return f"Mission requires review because: {reason}."


def _local_replan_operator_notes(action: str, spec: dict[str, Any], route_override: list[str] | None) -> list[str]:
    notes: list[str] = []
    summary = str(spec.get("summary") or spec.get("type") or "task")
    if action == "reroute" and route_override:
        notes.append(f"{summary} will follow the reviewed route override before execution resumes.")
    if action == "use_fallback":
        notes.append("Fallback reassignment preserves the existing step order and mission dependencies.")
    if action == "retry":
        notes.append("Retry is appropriate only if the blocking condition is temporary or has been cleared.")
    if spec.get("minimum_battery_level") is not None:
        notes.append(f"Mission still expects a robot above the configured battery threshold of {spec['minimum_battery_level']}.")
    return list(dict.fromkeys(notes))
