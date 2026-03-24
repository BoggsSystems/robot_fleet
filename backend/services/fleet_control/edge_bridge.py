"""
Local DDS-to-event bridge scaffold.

This bridge currently pulls normalized state from RobotManager and publishes
canonical events through a transport-neutral sink. A cloud-specific MQTT client
can be added later without changing the event contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Callable, Protocol

from data.log_utils import log_robot_status

from .config import LocalRuntimeConfig
from .events import (
    CanonicalEvent,
    RobotHealthPayload,
    RobotTelemetryPayload,
    event_from_dict,
    event_from_payload,
    make_metadata,
)
from .robot_manager import STATUS_DISCONNECTED, STATUS_ERROR, RobotManager


class EventSink(Protocol):
    """Minimal interface for any local or cloud event transport."""

    def publish(self, topic: str, event: CanonicalEvent) -> None:
        ...


@dataclass
class RecordedPublication:
    """One published event recorded by the local in-memory sink."""

    topic: str
    event: dict[str, Any]


@dataclass
class InMemoryEventSink:
    """Simple local sink for tests, debugging, and projection wiring."""

    publications: list[RecordedPublication] = field(default_factory=list)

    def publish(self, topic: str, event: CanonicalEvent) -> None:
        self.publications.append(RecordedPublication(topic=topic, event=event.to_dict()))


class JsonLinesEventSink:
    """Append canonical events to a JSONL file for replay and debugging."""

    def __init__(self, path: str):
        self.path = path

    def publish(self, topic: str, event: CanonicalEvent) -> None:
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps({"topic": topic, "event": event.to_dict()}) + "\n")


class MqttEventSink:
    """Optional MQTT sink for Mosquitto-backed local testing."""

    def __init__(self, host: str, port: int):
        try:
            import paho.mqtt.client as mqtt
        except ImportError as exc:
            raise RuntimeError(
                "paho-mqtt is required for MqttEventSink. Install it before using the MQTT adapter."
            ) from exc

        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._client.connect(host, port, keepalive=30)
        self._client.loop_start()

    def publish(self, topic: str, event: CanonicalEvent) -> None:
        result = self._client.publish(topic, event.to_json(), qos=0, retain=False)
        result.wait_for_publish()

    def close(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()


class MqttEventSubscriber:
    """Subscribe to canonical events over MQTT and hand them to a callback."""

    def __init__(self, host: str, port: int, topic_filter: str, on_event: Callable[[str, CanonicalEvent], None]):
        try:
            import paho.mqtt.client as mqtt
        except ImportError as exc:
            raise RuntimeError(
                "paho-mqtt is required for MqttEventSubscriber. Install it before using the MQTT subscriber."
            ) from exc

        self._topic_filter = topic_filter
        self._on_event = on_event
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self._client.on_connect = self._handle_connect
        self._client.on_message = self._handle_message
        self._client.connect(host, port, keepalive=30)

    def _handle_connect(self, client, _userdata, _flags, reason_code, _properties) -> None:
        if reason_code == 0:
            client.subscribe(self._topic_filter)

    def _handle_message(self, _client, _userdata, message) -> None:
        payload = json.loads(message.payload.decode("utf-8"))
        event = event_from_dict(payload)
        self._on_event(message.topic, event)

    def loop_start(self) -> None:
        self._client.loop_start()

    def loop_stop(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()


class LocalRobotEventBridge:
    """Bridge a RobotManager status snapshot into canonical events."""

    def __init__(
        self,
        robot_manager: RobotManager,
        config: LocalRuntimeConfig,
        sink: EventSink,
        *,
        source: str = "edge.robot_manager",
    ):
        self.robot_manager = robot_manager
        self.config = config
        self.sink = sink
        self.source = source
        self._sequence = 0

    def poll_once(self) -> list[CanonicalEvent]:
        """Poll one robot status snapshot and publish telemetry and health events."""
        status = self.robot_manager.get_status()
        robot_id = self.robot_manager.robot_id
        log_robot_status(robot_id, status)

        telemetry = self._build_telemetry_event(status)
        health = self._build_health_event(status)
        events = [telemetry, health]

        for event in events:
            topic = self.config.topic_for(robot_id, event.metadata.event_type)
            self.sink.publish(topic, event)

        return events

    def _build_telemetry_event(self, status: dict[str, Any]) -> CanonicalEvent:
        payload = RobotTelemetryPayload(
            status=status.get("status", STATUS_DISCONNECTED),
            battery_pct=_coerce_battery(status.get("battery")),
            pose=_normalize_pose(status.get("pose")),
            robot_type=status.get("robot_type", self.robot_manager.robot_type),
            robot_category=status.get("robot_category", self.robot_manager.robot_category),
            vendor=status.get("vendor", self.robot_manager.vendor),
            velocity=_normalize_velocity(status.get("velocity")),
        )
        return event_from_payload(self._next_metadata("robot.telemetry"), payload)

    def _build_health_event(self, status: dict[str, Any]) -> CanonicalEvent:
        battery = _coerce_battery(status.get("battery"))
        connectivity = "connected" if status.get("status") != STATUS_DISCONNECTED else "disconnected"
        active_alerts: list[str] = []
        health_status = "ok"
        if status.get("status") == STATUS_ERROR:
            health_status = "faulted"
            active_alerts.append("robot_status_error")
        if battery is not None and battery < 20:
            health_status = "warning"
            active_alerts.append("low_battery")
        payload = RobotHealthPayload(
            connectivity=connectivity,
            battery_pct=battery,
            health_status=health_status,
            active_alerts=active_alerts,
        )
        return event_from_payload(self._next_metadata("robot.health"), payload)

    def _next_metadata(self, event_type: str):
        self._sequence += 1
        return make_metadata(
            event_type=event_type,
            source=self.source,
            robot_id=self.robot_manager.robot_id,
            fleet_id=self.config.fleet_id,
            site_id=self.config.site_id,
            tenant_id=self.config.tenant_id,
            schema_version=self.config.schema_version,
            sequence=self._sequence,
        )


def _coerce_battery(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _normalize_pose(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        return {"x": 0.0, "y": 0.0, "theta": 0.0}
    return {
        "x": float(value.get("x", 0.0)),
        "y": float(value.get("y", 0.0)),
        "theta": float(value.get("theta", 0.0)),
    }


def _normalize_velocity(value: Any) -> list[float] | None:
    if not isinstance(value, list):
        return None
    normalized = []
    for item in value[:3]:
        try:
            normalized.append(float(item))
        except (TypeError, ValueError):
            normalized.append(0.0)
    return normalized
