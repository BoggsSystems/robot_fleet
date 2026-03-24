"""
Local mock twin projection service.

This module acts as a local stand-in for Azure Digital Twins so event projection
logic can be validated before any cloud resources exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .events import CanonicalEvent


@dataclass
class MockTwinStore:
    """In-memory representation of robot twins and recent events."""

    robots: dict[str, dict[str, Any]] = field(default_factory=dict)
    recent_events: list[dict[str, Any]] = field(default_factory=list)

    def upsert_robot(self, robot_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        robot_twin = self.robots.setdefault(
            robot_id,
            {
                "robotId": robot_id,
                "state": {},
                "health": {},
                "tasks": {},
                "alerts": [],
                "lastEventAt": None,
            },
        )
        robot_twin.update(patch)
        return robot_twin

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable view of current twin state."""
        return {
            "robots": self.robots,
            "recent_events": self.recent_events[-50:],
        }


class LocalTwinProjector:
    """Project canonical events into an in-memory twin model."""

    def __init__(self, store: MockTwinStore | None = None):
        self.store = store or MockTwinStore()

    def ingest(self, event: CanonicalEvent) -> dict[str, Any]:
        metadata = event.metadata
        payload = event.payload
        robot_id = metadata.robot_id

        self.store.recent_events.append(event.to_dict())
        twin = self.store.upsert_robot(
            robot_id,
            {
                "fleetId": metadata.fleet_id,
                "siteId": metadata.site_id,
                "tenantId": metadata.tenant_id,
                "lastEventAt": metadata.occurred_at,
            },
        )

        if metadata.event_type == "robot.telemetry":
            twin["state"] = {
                "status": payload.get("status"),
                "batteryPct": payload.get("battery_pct"),
                "pose": payload.get("pose", {}),
                "velocity": payload.get("velocity"),
                "robotType": payload.get("robot_type"),
                "robotCategory": payload.get("robot_category"),
                "vendor": payload.get("vendor"),
            }
        elif metadata.event_type == "robot.health":
            twin["health"] = {
                "connectivity": payload.get("connectivity"),
                "batteryPct": payload.get("battery_pct"),
                "healthStatus": payload.get("health_status"),
                "activeAlerts": payload.get("active_alerts", []),
            }
        elif metadata.event_type == "robot.task_status":
            task_id = payload.get("task_id", "unknown-task")
            twin.setdefault("tasks", {})[task_id] = {
                "taskStatus": payload.get("task_status"),
                "summary": payload.get("summary"),
                "details": payload.get("details", {}),
            }
        elif metadata.event_type == "robot.alert":
            twin.setdefault("alerts", []).append(
                {
                    "severity": payload.get("severity"),
                    "code": payload.get("code"),
                    "message": payload.get("message"),
                    "details": payload.get("details", {}),
                    "occurredAt": metadata.occurred_at,
                }
            )

        return twin

    def project_many(self, events: list[CanonicalEvent]) -> dict[str, Any]:
        """Project a sequence of events and return a final store snapshot."""
        for event in events:
            self.ingest(event)
        return self.store.snapshot()
