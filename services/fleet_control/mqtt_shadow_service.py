"""
MQTT-backed consumer path for the Shadow World runtime.
"""

from __future__ import annotations

import time

from .config import LocalRuntimeConfig
from .edge_bridge import MqttEventSubscriber
from .events import CanonicalEvent
from .shadow_service import ShadowWorldService


class MqttShadowWorldService:
    """Subscribe to local MQTT topics and project events like a backend worker."""

    def __init__(self, config: LocalRuntimeConfig | None = None):
        self.config = config or LocalRuntimeConfig()
        self.service = ShadowWorldService()
        self._subscriber = MqttEventSubscriber(
            host=self.config.mqtt_host,
            port=self.config.mqtt_port,
            topic_filter=f"{self.config.mqtt_root}/#",
            on_event=self._handle_event,
        )
        self._consumed_count = 0

    def _handle_event(self, _topic: str, event: CanonicalEvent) -> None:
        self.service.consume([event], topic=_topic)
        self._consumed_count += 1

    def run_for(self, seconds: float = 2.0) -> dict:
        """Run the subscriber for a short window and return the current projection."""
        self._subscriber.loop_start()
        try:
            time.sleep(seconds)
        finally:
            self._subscriber.loop_stop()
        snapshot = self.service.projector.store.snapshot()
        return {
            "consumed_count": self._consumed_count,
            "twin_snapshot": snapshot,
        }
