"""
Local runner for the Phase 1 Shadow World scaffold.

This can be used from the command line to verify event creation and mock twin
projection without any Azure resources or MQTT dependencies.
"""

from __future__ import annotations

import json
from pathlib import Path
import time

from .config import LocalRuntimeConfig
from .controller import FleetController
from .edge_bridge import InMemoryEventSink, JsonLinesEventSink, LocalRobotEventBridge
from .events import event_from_dict
from .mock_twin import LocalTwinProjector
from .pilot_module import DEFAULT_TASK_SPECS, run_single_task
from .persistence import ShadowWorldStore
from .robot_manager import RobotManager
from .shadow_service import ShadowWorldService, replay_jsonl


class CanonicalEventProxy:
    """Minimal adapter to reuse JSONL sink with serialized in-memory publications."""

    def __init__(self, event_dict: dict):
        self._event_dict = event_dict

    def to_dict(self) -> dict:
        return self._event_dict


def run_local_cycle() -> dict:
    """Run one local edge->event->twin projection cycle for a simulated robot."""
    robot = RobotManager(robot_id="g1-001", sim=True, robot_type="unitree_g1")
    robot.connect()

    config = LocalRuntimeConfig()
    sink = InMemoryEventSink()
    bridge = LocalRobotEventBridge(robot_manager=robot, config=config, sink=sink)
    projector = LocalTwinProjector()

    for event in bridge.poll_once():
        projector.ingest(event)

    return {
        "published": [publication.event for publication in sink.publications],
        "twin_snapshot": projector.store.snapshot(),
    }


def run_local_service_loop(cycles: int = 3, sleep_sec: float = 0.1) -> dict:
    """Run a short local loop with telemetry and task lifecycle projection."""
    robot = RobotManager(robot_id="g1-001", sim=True, robot_type="unitree_g1")
    robot.connect()

    config = LocalRuntimeConfig()
    sink = InMemoryEventSink()
    projector = LocalTwinProjector()
    store = ShadowWorldStore()
    store.reset()
    service = ShadowWorldService(projector=projector, store=store)
    bridge = LocalRobotEventBridge(robot_manager=robot, config=config, sink=sink)
    controller = FleetController(runtime_config=config)
    controller.register_robot(robot.robot_id, robot_manager=robot)

    replay_path = "data/logs/shadow_world_events.jsonl"
    replay_file = Path(replay_path)
    replay_file.parent.mkdir(parents=True, exist_ok=True)
    replay_file.write_text("", encoding="utf-8")
    jsonl_sink = JsonLinesEventSink(replay_path)

    for index in range(cycles):
        publication_count_before = len(sink.publications)
        events = bridge.poll_once()
        for event in events:
            service.consume([event], topic=config.topic_for(robot.robot_id, event.metadata.event_type))
            jsonl_sink.publish(config.topic_for(robot.robot_id, event.metadata.event_type), event)

        if index < len(DEFAULT_TASK_SPECS):
            task_spec = DEFAULT_TASK_SPECS[index]
            task_id = f"shadow-task-{index}"
            controller.assign_task(task_id, robot.robot_id, task_spec)
            run_single_task(
                controller,
                robot.robot_id,
                task_id,
                task_spec,
                projector=projector,
                sink=sink,
            )

        for publication in sink.publications[publication_count_before:]:
            jsonl_sink.publish(publication.topic, CanonicalEventProxy(publication.event))
            service.consume([event_from_dict(publication.event)], topic=publication.topic)

        time.sleep(sleep_sec)

    return {
        "published_count": len(sink.publications),
        "twin_snapshot": projector.store.snapshot(),
        "event_log_path": replay_path,
        "replay_preview": replay_jsonl(replay_path),
        "persisted_events": len(store.recent_events(100)),
    }


if __name__ == "__main__":
    print(json.dumps(run_local_service_loop(), indent=2))
