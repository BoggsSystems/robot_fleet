"""
Local event consumer and replay service for the Shadow World runtime.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .adt_adapter import TwinProjectionAdapter
from .events import CanonicalEvent, event_from_dict
from .mock_twin import LocalTwinProjector
from .persistence import ShadowWorldStore
from .twin_mapper import TwinMapper


class JsonlReplayConsumer:
    """Consume JSONL event logs produced by the local edge runtime."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def read_events(self) -> list[CanonicalEvent]:
        if not self.path.exists():
            return []

        events: list[CanonicalEvent] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                events.append(event_from_dict(record["event"]))
        return events


class ShadowWorldService:
    """Consume canonical events and build both local twin and ADT-style patches."""

    def __init__(
        self,
        projector: LocalTwinProjector | None = None,
        mapper: TwinMapper | None = None,
        store: ShadowWorldStore | None = None,
        adt_adapter: TwinProjectionAdapter | None = None,
    ):
        self.projector = projector or LocalTwinProjector()
        self.mapper = mapper or TwinMapper()
        self.store = store or ShadowWorldStore()
        self.adt_adapter = adt_adapter

    def consume(self, events: Iterable[CanonicalEvent], *, topic: str | None = None) -> dict:
        patches = []
        adt_operations = []
        count = 0
        for event in events:
            twin = self.projector.ingest(event)
            document = self.mapper.map_event(event)
            patch = document.to_dict()
            self.store.persist_event(event, topic=topic)
            self.store.persist_robot_snapshot(event.metadata.robot_id, twin)
            self.store.persist_patch(
                event.metadata.event_id,
                event.metadata.robot_id,
                event.metadata.event_type,
                patch,
            )
            if self.adt_adapter is not None:
                adt_operations.append(self.adt_adapter.apply_patch(document))
            patches.append(patch)
            count += 1
        return {
            "consumed_count": count,
            "twin_snapshot": self.projector.store.snapshot(),
            "adt_patch_preview": patches[-20:],
            "adt_operation_preview": adt_operations[-20:],
        }


def replay_jsonl(path: str | Path) -> dict:
    """Replay a JSONL event file through the local service."""
    consumer = JsonlReplayConsumer(path)
    service = ShadowWorldService()
    service.store.reset()
    return service.consume(consumer.read_events())
