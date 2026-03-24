"""
Local runtime configuration for the Shadow World bridge.

These settings stay cloud-neutral so the same event contracts can be promoted to
Azure IoT Operations and Azure Digital Twins later.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalRuntimeConfig:
    """Configuration for local edge runtime and topic naming."""

    fleet_id: str = "fleet-alpha"
    site_id: str = "site-local-dev"
    tenant_id: str = "boggs-systems"
    mqtt_host: str = "127.0.0.1"
    mqtt_port: int = 1883
    mqtt_root: str = "fleet"
    schema_version: str = "2026-03-18"

    def topic_for(self, robot_id: str, event_name: str) -> str:
        """Return a canonical topic path for robot-originated events."""
        return f"{self.mqtt_root}/{self.site_id}/{self.fleet_id}/robots/{robot_id}/{event_name}"

    def command_topic_for(self, robot_id: str) -> str:
        """Return canonical topic path for command events."""
        return f"{self.mqtt_root}/{self.site_id}/{self.fleet_id}/robots/{robot_id}/commands"
