"""
Map canonical events into Azure Digital Twins-oriented projection documents.

This does not call Azure yet. It produces the patch shape and relationship data a
future ADT adapter can send to Digital Twins.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .events import CanonicalEvent, TwinProjectionPayload


@dataclass(frozen=True)
class TwinPatchDocument:
    """A lightweight ADT-style patch description."""

    twin_id: str
    model_id: str
    patch: list[dict[str, Any]]
    relationships: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TwinMapper:
    """Convert canonical events into ADT-oriented patch documents."""

    ROBOT_MODEL_ID = "dtmi:boggssystems:robotfleet:UnitreeG1;1"

    def map_event(self, event: CanonicalEvent) -> TwinPatchDocument:
        metadata = event.metadata
        payload = event.payload
        twin_id = f"robot:{metadata.robot_id}"
        patch: list[dict[str, Any]] = []
        relationships: list[dict[str, Any]] = [
            {
                "relationshipName": "belongsToFleet",
                "targetId": f"fleet:{metadata.fleet_id}",
            },
            {
                "relationshipName": "locatedAtSite",
                "targetId": f"site:{metadata.site_id}",
            },
        ]

        if metadata.event_type == "robot.telemetry":
            patch.extend(
                [
                    {"op": "add", "path": "/status", "value": payload.get("status")},
                    {"op": "add", "path": "/batteryPct", "value": payload.get("battery_pct")},
                    {"op": "add", "path": "/pose", "value": payload.get("pose", {})},
                    {"op": "add", "path": "/velocity", "value": payload.get("velocity")},
                    {"op": "add", "path": "/robotType", "value": payload.get("robot_type")},
                    {"op": "add", "path": "/robotCategory", "value": payload.get("robot_category")},
                    {"op": "add", "path": "/vendor", "value": payload.get("vendor")},
                ]
            )
        elif metadata.event_type == "robot.health":
            patch.extend(
                [
                    {"op": "add", "path": "/health/connectivity", "value": payload.get("connectivity")},
                    {"op": "add", "path": "/health/batteryPct", "value": payload.get("battery_pct")},
                    {"op": "add", "path": "/health/healthStatus", "value": payload.get("health_status")},
                    {"op": "add", "path": "/health/activeAlerts", "value": payload.get("active_alerts", [])},
                ]
            )
        elif metadata.event_type == "robot.task_status":
            task_id = payload.get("task_id", "unknown-task")
            patch.append(
                {
                    "op": "add",
                    "path": f"/tasks/{task_id}",
                    "value": {
                        "taskStatus": payload.get("task_status"),
                        "summary": payload.get("summary"),
                        "details": payload.get("details", {}),
                    },
                }
            )
            relationships.append(
                {
                    "relationshipName": "assignedToTask",
                    "targetId": f"task:{task_id}",
                }
            )
        elif metadata.event_type == "robot.alert":
            code = payload.get("code", "unknown-alert")
            patch.append(
                {
                    "op": "add",
                    "path": "/alerts/-",
                    "value": {
                        "severity": payload.get("severity"),
                        "code": code,
                        "message": payload.get("message"),
                        "details": payload.get("details", {}),
                        "occurredAt": metadata.occurred_at,
                    },
                }
            )

        patch.append({"op": "add", "path": "/lastEventAt", "value": metadata.occurred_at})
        return TwinPatchDocument(
            twin_id=twin_id,
            model_id=self.ROBOT_MODEL_ID,
            patch=patch,
            relationships=relationships,
        )

    def projection_payload(self, event: CanonicalEvent) -> TwinProjectionPayload:
        """Return a projection record useful for logs or downstream services."""
        document = self.map_event(event)
        return TwinProjectionPayload(
            entity_type="robot",
            entity_id=document.twin_id,
            projection_type=event.metadata.event_type,
            fields={
                "modelId": document.model_id,
                "patch": document.patch,
                "relationships": document.relationships,
            },
        )
