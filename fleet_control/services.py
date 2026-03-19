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
        current["status"] = status
        if result is not None:
            current["result"] = result
        current["updated_at"] = _utc_now_iso()
        self.store.upsert_task_record(current)
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

        controller.assign_task(task_id, robot_id, {"type": task["task_type"], "params": task["spec"]})
        result = run_single_task(controller, robot_id, task_id, {"type": task["task_type"], "params": task["spec"]})
        final_status = "completed" if result.get("success") else "failed"
        updated = self.update_task_status(task_id, final_status, result=result)
        self.update_robot_status(robot_id, "idle")
        return updated

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
