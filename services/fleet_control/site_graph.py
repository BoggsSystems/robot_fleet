"""
Local operational site-graph loader for the manually authored cottage model.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


DEFAULT_SITE_MODEL_PATH = Path(__file__).resolve().parent.parent / "docs" / "cottage" / "parents-cottage-site-model.json"


@dataclass(frozen=True)
class SiteNode:
    node_id: str
    label: str
    node_type: str
    environment: str
    site_id: str
    aliases: tuple[str, ...]
    raw: dict[str, Any]


class SiteGraph:
    def __init__(self, payload: dict[str, Any], *, source_path: Path):
        self.source_path = source_path
        nodes = []
        alias_index: dict[str, str] = {}
        for record in payload.get("nodes", []):
            node = SiteNode(
                node_id=record["id"],
                label=record.get("label", record["id"]),
                node_type=record.get("nodeType", "zone"),
                environment=record.get("environment", "unknown"),
                site_id=record.get("siteId", ""),
                aliases=tuple(_node_aliases(record)),
                raw=record,
            )
            nodes.append(node)
            for alias in node.aliases:
                alias_index.setdefault(alias, node.node_id)

        adjacency: dict[str, set[str]] = {node.node_id: set() for node in nodes}
        for edge in payload.get("edges", []):
            left = edge.get("from")
            right = edge.get("to")
            if left in adjacency and right in adjacency:
                adjacency[left].add(right)
                adjacency[right].add(left)

        self.nodes = {node.node_id: node for node in nodes}
        self.alias_index = alias_index
        self.adjacency = adjacency
        self.routes = payload.get("workflowRoutes", [])
        self.raw = payload

    def resolve_node_id(self, value: str | None) -> str | None:
        if not value:
            return None
        normalized = _normalize(value)
        if normalized in self.alias_index:
            return self.alias_index[normalized]
        if value in self.nodes:
            return value
        return None

    def route_between(self, source: str | None, destination: str | None, *, blocked_node: str | None = None) -> list[str] | None:
        source_id = self.resolve_node_id(source)
        destination_id = self.resolve_node_id(destination)
        if not source_id or not destination_id:
            return None
        if source_id == destination_id:
            return [source_id]

        blocked_id = self.resolve_node_id(blocked_node) if blocked_node else None
        if blocked_id in {source_id, destination_id}:
            return None

        queue: deque[tuple[str, list[str]]] = deque([(source_id, [source_id])])
        visited = {source_id}
        while queue:
            current, path = queue.popleft()
            for neighbor in sorted(self.adjacency.get(current, ())):
                if neighbor in visited or neighbor == blocked_id:
                    continue
                next_path = path + [neighbor]
                if neighbor == destination_id:
                    return next_path
                visited.add(neighbor)
                queue.append((neighbor, next_path))
        return None

    def known_zone_terms(self) -> list[str]:
        values = []
        for node in self.nodes.values():
            values.extend(node.aliases)
            values.append(_normalize(node.label))
        return sorted(set(values))

    def route_labels(self, route: list[str] | None) -> list[str]:
        if not route:
            return []
        return [self.nodes.get(node_id, SiteNode(node_id, node_id, "unknown", "unknown", "", (), {})).label for node_id in route]


@lru_cache(maxsize=1)
def load_default_site_graph() -> SiteGraph:
    with DEFAULT_SITE_MODEL_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return SiteGraph(payload, source_path=DEFAULT_SITE_MODEL_PATH)


def _normalize(value: str) -> str:
    return value.strip().lower().replace("_", " ").replace("-", " ")


def _node_aliases(record: dict[str, Any]) -> list[str]:
    aliases = [_normalize(alias) for alias in record.get("aliases", []) if isinstance(alias, str)]
    aliases.append(_normalize(record.get("label", record["id"])))
    aliases.append(_normalize(record["id"]))
    return sorted(set(alias for alias in aliases if alias))
