"""
Persistent local storage for Shadow World events, projected state, and Phase 3
fleet backend entities.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .events import CanonicalEvent


DEFAULT_DB_PATH = Path("data/shadow_world.db")


class ShadowWorldStore:
    """SQLite-backed store for canonical events, current robot state, and registries."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS canonical_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    robot_id TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    topic TEXT,
                    event_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS robot_state (
                    robot_id TEXT PRIMARY KEY,
                    fleet_id TEXT NOT NULL,
                    site_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS twin_patches (
                    event_id TEXT PRIMARY KEY,
                    robot_id TEXT NOT NULL,
                    projection_type TEXT NOT NULL,
                    patch_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS fleets (
                    fleet_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sites (
                    site_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS zones (
                    zone_id TEXT PRIMARY KEY,
                    site_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    parent_zone_id TEXT,
                    zone_type TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS robots (
                    robot_id TEXT PRIMARY KEY,
                    fleet_id TEXT NOT NULL,
                    site_id TEXT NOT NULL,
                    zone_id TEXT,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    network_interface TEXT NOT NULL,
                    model TEXT NOT NULL,
                    serial TEXT NOT NULL,
                    firmware TEXT NOT NULL,
                    robot_type TEXT NOT NULL,
                    robot_category TEXT NOT NULL,
                    vendor TEXT NOT NULL,
                    capabilities_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    robot_id TEXT,
                    fleet_id TEXT NOT NULL,
                    site_id TEXT NOT NULL,
                    zone_id TEXT,
                    task_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    spec_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS commands (
                    command_id TEXT PRIMARY KEY,
                    robot_id TEXT NOT NULL,
                    command_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    parameters_json TEXT NOT NULL,
                    issued_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS onboarding_records (
                    robot_id TEXT PRIMARY KEY,
                    stage TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mission_sessions (
                    mission_id TEXT PRIMARY KEY,
                    request_text TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    status TEXT NOT NULL,
                    preview_json TEXT NOT NULL,
                    question_json TEXT NOT NULL,
                    task_ids_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def reset(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM canonical_events")
            conn.execute("DELETE FROM robot_state")
            conn.execute("DELETE FROM twin_patches")
            conn.execute("DELETE FROM fleets")
            conn.execute("DELETE FROM sites")
            conn.execute("DELETE FROM zones")
            conn.execute("DELETE FROM robots")
            conn.execute("DELETE FROM tasks")
            conn.execute("DELETE FROM commands")
            conn.execute("DELETE FROM onboarding_records")
            conn.execute("DELETE FROM mission_sessions")

    def persist_event(self, event: CanonicalEvent, topic: str | None = None) -> None:
        payload = event.to_json()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO canonical_events (
                    event_id, event_type, robot_id, occurred_at, topic, event_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event.metadata.event_id,
                    event.metadata.event_type,
                    event.metadata.robot_id,
                    event.metadata.occurred_at,
                    topic,
                    payload,
                ),
            )

    def persist_robot_snapshot(self, robot_id: str, snapshot: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO robot_state (
                    robot_id, fleet_id, site_id, tenant_id, state_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    robot_id,
                    snapshot.get("fleetId", ""),
                    snapshot.get("siteId", ""),
                    snapshot.get("tenantId", ""),
                    json.dumps(snapshot),
                    snapshot.get("lastEventAt", ""),
                ),
            )

    def persist_patch(self, event_id: str, robot_id: str, projection_type: str, patch: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO twin_patches (
                    event_id, robot_id, projection_type, patch_json, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    robot_id,
                    projection_type,
                    json.dumps(patch),
                    patch.get("patch", [{}])[-1].get("value", ""),
                ),
            )

    def recent_events(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT event_json FROM canonical_events
                ORDER BY occurred_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def current_robot_states(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT state_json FROM robot_state
                ORDER BY robot_id ASC
                """
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def recent_patches(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT patch_json FROM twin_patches
                ORDER BY rowid DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def upsert_fleet(self, fleet: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO fleets (
                    fleet_id, name, status, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    fleet["fleet_id"],
                    fleet["name"],
                    fleet["status"],
                    json.dumps(fleet.get("metadata", {})),
                    fleet["created_at"],
                    fleet["updated_at"],
                ),
            )

    def list_fleets(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT fleet_id, name, status, metadata_json, created_at, updated_at FROM fleets ORDER BY fleet_id"
            ).fetchall()
        return [
            {
                "fleet_id": row[0],
                "name": row[1],
                "status": row[2],
                "metadata": json.loads(row[3]),
                "created_at": row[4],
                "updated_at": row[5],
            }
            for row in rows
        ]

    def upsert_site(self, site: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO sites (
                    site_id, name, status, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    site["site_id"],
                    site["name"],
                    site["status"],
                    json.dumps(site.get("metadata", {})),
                    site["created_at"],
                    site["updated_at"],
                ),
            )

    def list_sites(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT site_id, name, status, metadata_json, created_at, updated_at FROM sites ORDER BY site_id"
            ).fetchall()
        return [
            {
                "site_id": row[0],
                "name": row[1],
                "status": row[2],
                "metadata": json.loads(row[3]),
                "created_at": row[4],
                "updated_at": row[5],
            }
            for row in rows
        ]

    def upsert_zone(self, zone: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO zones (
                    zone_id, site_id, name, parent_zone_id, zone_type, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    zone["zone_id"],
                    zone["site_id"],
                    zone["name"],
                    zone.get("parent_zone_id"),
                    zone["zone_type"],
                    json.dumps(zone.get("metadata", {})),
                    zone["created_at"],
                    zone["updated_at"],
                ),
            )

    def list_zones(self, site_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT zone_id, site_id, name, parent_zone_id, zone_type, metadata_json, created_at, updated_at FROM zones"
        params: tuple[Any, ...] = ()
        if site_id:
            query += " WHERE site_id = ?"
            params = (site_id,)
        query += " ORDER BY zone_id"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {
                "zone_id": row[0],
                "site_id": row[1],
                "name": row[2],
                "parent_zone_id": row[3],
                "zone_type": row[4],
                "metadata": json.loads(row[5]),
                "created_at": row[6],
                "updated_at": row[7],
            }
            for row in rows
        ]

    def upsert_robot_record(self, robot: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO robots (
                    robot_id, fleet_id, site_id, zone_id, name, status, ip_address, network_interface,
                    model, serial, firmware, robot_type, robot_category, vendor, capabilities_json,
                    metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    robot["robot_id"],
                    robot["fleet_id"],
                    robot["site_id"],
                    robot.get("zone_id"),
                    robot["name"],
                    robot["status"],
                    robot["ip_address"],
                    robot["network_interface"],
                    robot["model"],
                    robot["serial"],
                    robot["firmware"],
                    robot["robot_type"],
                    robot["robot_category"],
                    robot["vendor"],
                    json.dumps(robot.get("capabilities", [])),
                    json.dumps(robot.get("metadata", {})),
                    robot["created_at"],
                    robot["updated_at"],
                ),
            )

    def get_robot_record(self, robot_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT robot_id, fleet_id, site_id, zone_id, name, status, ip_address, network_interface,
                       model, serial, firmware, robot_type, robot_category, vendor, capabilities_json,
                       metadata_json, created_at, updated_at
                FROM robots WHERE robot_id = ?
                """,
                (robot_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "robot_id": row[0],
            "fleet_id": row[1],
            "site_id": row[2],
            "zone_id": row[3],
            "name": row[4],
            "status": row[5],
            "ip_address": row[6],
            "network_interface": row[7],
            "model": row[8],
            "serial": row[9],
            "firmware": row[10],
            "robot_type": row[11],
            "robot_category": row[12],
            "vendor": row[13],
            "capabilities": json.loads(row[14]),
            "metadata": json.loads(row[15]),
            "created_at": row[16],
            "updated_at": row[17],
        }

    def update_robot_record_status(self, robot_id: str, status: str, zone_id: str | None = None) -> dict[str, Any]:
        robot = self.get_robot_record(robot_id)
        if robot is None:
            raise ValueError(f"Robot {robot_id} not found")
        robot["status"] = status
        if zone_id is not None:
            robot["zone_id"] = zone_id
        robot["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.upsert_robot_record(robot)
        return robot

    def list_robot_records(self, fleet_id: str | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT robot_id, fleet_id, site_id, zone_id, name, status, ip_address, network_interface,
                   model, serial, firmware, robot_type, robot_category, vendor, capabilities_json,
                   metadata_json, created_at, updated_at
            FROM robots
        """
        params: tuple[Any, ...] = ()
        if fleet_id:
            query += " WHERE fleet_id = ?"
            params = (fleet_id,)
        query += " ORDER BY robot_id"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {
                "robot_id": row[0],
                "fleet_id": row[1],
                "site_id": row[2],
                "zone_id": row[3],
                "name": row[4],
                "status": row[5],
                "ip_address": row[6],
                "network_interface": row[7],
                "model": row[8],
                "serial": row[9],
                "firmware": row[10],
                "robot_type": row[11],
                "robot_category": row[12],
                "vendor": row[13],
                "capabilities": json.loads(row[14]),
                "metadata": json.loads(row[15]),
                "created_at": row[16],
                "updated_at": row[17],
            }
            for row in rows
        ]

    def upsert_task_record(self, task: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tasks (
                    task_id, robot_id, fleet_id, site_id, zone_id, task_type, status, spec_json,
                    result_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task["task_id"],
                    task.get("robot_id"),
                    task["fleet_id"],
                    task["site_id"],
                    task.get("zone_id"),
                    task["task_type"],
                    task["status"],
                    json.dumps(task.get("spec", {})),
                    json.dumps(task.get("result", {})),
                    task["created_at"],
                    task["updated_at"],
                ),
            )

    def get_task_record(self, task_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT task_id, robot_id, fleet_id, site_id, zone_id, task_type, status, spec_json, result_json, created_at, updated_at
                FROM tasks WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "task_id": row[0],
            "robot_id": row[1],
            "fleet_id": row[2],
            "site_id": row[3],
            "zone_id": row[4],
            "task_type": row[5],
            "status": row[6],
            "spec": json.loads(row[7]),
            "result": json.loads(row[8]),
            "created_at": row[9],
            "updated_at": row[10],
        }

    def list_task_records(self, status: str | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT task_id, robot_id, fleet_id, site_id, zone_id, task_type, status, spec_json, result_json, created_at, updated_at
            FROM tasks
        """
        params: tuple[Any, ...] = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY updated_at DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {
                "task_id": row[0],
                "robot_id": row[1],
                "fleet_id": row[2],
                "site_id": row[3],
                "zone_id": row[4],
                "task_type": row[5],
                "status": row[6],
                "spec": json.loads(row[7]),
                "result": json.loads(row[8]),
                "created_at": row[9],
                "updated_at": row[10],
            }
            for row in rows
        ]

    def upsert_command_record(self, command: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO commands (
                    command_id, robot_id, command_type, status, parameters_json, issued_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    command["command_id"],
                    command["robot_id"],
                    command["command_type"],
                    command["status"],
                    json.dumps(command.get("parameters", {})),
                    command["issued_by"],
                    command["created_at"],
                    command["updated_at"],
                ),
            )

    def get_command_record(self, command_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT command_id, robot_id, command_type, status, parameters_json, issued_by, created_at, updated_at
                FROM commands WHERE command_id = ?
                """,
                (command_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "command_id": row[0],
            "robot_id": row[1],
            "command_type": row[2],
            "status": row[3],
            "parameters": json.loads(row[4]),
            "issued_by": row[5],
            "created_at": row[6],
            "updated_at": row[7],
        }

    def list_command_records(self, robot_id: str | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT command_id, robot_id, command_type, status, parameters_json, issued_by, created_at, updated_at
            FROM commands
        """
        params: tuple[Any, ...] = ()
        if robot_id:
            query += " WHERE robot_id = ?"
            params = (robot_id,)
        query += " ORDER BY updated_at DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {
                "command_id": row[0],
                "robot_id": row[1],
                "command_type": row[2],
                "status": row[3],
                "parameters": json.loads(row[4]),
                "issued_by": row[5],
                "created_at": row[6],
                "updated_at": row[7],
            }
            for row in rows
        ]

    def upsert_onboarding_record(self, record: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO onboarding_records (
                    robot_id, stage, status, details_json, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record["robot_id"],
                    record["stage"],
                    record["status"],
                    json.dumps(record.get("details", {})),
                    record["updated_at"],
                ),
            )

    def get_onboarding_record(self, robot_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT robot_id, stage, status, details_json, updated_at
                FROM onboarding_records WHERE robot_id = ?
                """,
                (robot_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "robot_id": row[0],
            "stage": row[1],
            "status": row[2],
            "details": json.loads(row[3]),
            "updated_at": row[4],
        }

    def upsert_mission_session(self, session: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO mission_sessions (
                    mission_id, request_text, requested_by, status, preview_json, question_json,
                    task_ids_json, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["mission_id"],
                    session["request_text"],
                    session["requested_by"],
                    session["status"],
                    json.dumps(session.get("preview", {})),
                    json.dumps(session.get("question", {})),
                    json.dumps(session.get("task_ids", [])),
                    json.dumps(session.get("metadata", {})),
                    session["created_at"],
                    session["updated_at"],
                ),
            )

    def get_mission_session(self, mission_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT mission_id, request_text, requested_by, status, preview_json, question_json,
                       task_ids_json, metadata_json, created_at, updated_at
                FROM mission_sessions WHERE mission_id = ?
                """,
                (mission_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "mission_id": row[0],
            "request_text": row[1],
            "requested_by": row[2],
            "status": row[3],
            "preview": json.loads(row[4]),
            "question": json.loads(row[5]),
            "task_ids": json.loads(row[6]),
            "metadata": json.loads(row[7]),
            "created_at": row[8],
            "updated_at": row[9],
        }

    def list_mission_sessions(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT mission_id, request_text, requested_by, status, preview_json, question_json,
                       task_ids_json, metadata_json, created_at, updated_at
                FROM mission_sessions
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "mission_id": row[0],
                "request_text": row[1],
                "requested_by": row[2],
                "status": row[3],
                "preview": json.loads(row[4]),
                "question": json.loads(row[5]),
                "task_ids": json.loads(row[6]),
                "metadata": json.loads(row[7]),
                "created_at": row[8],
                "updated_at": row[9],
            }
            for row in rows
        ]
