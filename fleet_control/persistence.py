"""
Persistent local storage for Shadow World events and projected state.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .events import CanonicalEvent


DEFAULT_DB_PATH = Path("data/shadow_world.db")


class ShadowWorldStore:
    """SQLite-backed store for canonical events and current robot state."""

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

    def reset(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM canonical_events")
            conn.execute("DELETE FROM robot_state")
            conn.execute("DELETE FROM twin_patches")

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
