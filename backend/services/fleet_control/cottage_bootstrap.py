"""
Bootstrap helpers for a generic cottage Digital Twin graph.

These helpers provision a placeholder site graph before the real cottage layout
is known. The resulting twin seeds can be loaded into Azure Digital Twins or
used locally for planning and simulation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol


MODEL_IDS = {
    "site": "dtmi:boggssystems:cottagedomain:Site;1",
    "zone": "dtmi:boggssystems:cottagedomain:Zone;1",
    "path": "dtmi:boggssystems:cottagedomain:PathSegment;1",
    "building": "dtmi:boggssystems:cottagedomain:Building;1",
    "room": "dtmi:boggssystems:cottagedomain:Room;1",
    "dock": "dtmi:boggssystems:cottagedomain:Dock;1",
    "robot": "dtmi:boggssystems:cottagedomain:Robot;1",
    "boat": "dtmi:boggssystems:cottagedomain:Boat;1",
}


@dataclass(frozen=True)
class TwinSeed:
    """One twin instance to create during bootstrap."""

    twin_id: str
    model_id: str
    properties: dict[str, Any]

    def to_adt_payload(self) -> dict[str, Any]:
        payload = dict(self.properties)
        payload["$metadata"] = {"$model": self.model_id}
        return payload


@dataclass(frozen=True)
class RelationshipSeed:
    """One relationship instance to create during bootstrap."""

    source_id: str
    relationship_name: str
    target_id: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class TwinGraphProvisioner(Protocol):
    """Subset of adapter methods required to provision a graph."""

    def upsert_twin(self, twin_id: str, model_id: str, properties: dict[str, Any]) -> Any:
        ...

    def upsert_relationship(self, source_id: str, relationship_name: str, target_id: str) -> Any:
        ...


def build_placeholder_cottage_graph(site_slug: str = "parents-cottage") -> dict[str, list[dict[str, Any]]]:
    """Return a generic site graph that can be loaded before site intake is complete."""
    prefix = f"{site_slug}"
    twins = [
        TwinSeed(
            twin_id=f"site--{prefix}",
            model_id=MODEL_IDS["site"],
            properties={
                "siteId": f"site:{prefix}",
                "name": "Parents Cottage",
                "status": "planning",
                "timezone": "America/Toronto",
                "weatherSummary": "unknown",
                "lastUpdatedAt": "2026-03-19T00:00:00Z",
            },
        ),
        TwinSeed(
            twin_id=f"zone--{prefix}--landing",
            model_id=MODEL_IDS["zone"],
            properties={
                "siteId": f"site:{prefix}",
                "name": "Landing",
                "locationType": "zone",
                "status": "available",
                "surfaceType": "mixed",
                "hazardLevel": "unknown",
                "lastUpdatedAt": "2026-03-19T00:00:00Z",
            },
        ),
        TwinSeed(
            twin_id=f"path--{prefix}--landing-to-dock",
            model_id=MODEL_IDS["path"],
            properties={
                "siteId": f"site:{prefix}",
                "name": "Landing To Dock",
                "locationType": "path_segment",
                "status": "available",
                "distanceMeters": 30.0,
                "gradePct": 4.0,
                "isStairAccess": False,
                "lastUpdatedAt": "2026-03-19T00:00:00Z",
            },
        ),
        TwinSeed(
            twin_id=f"dock--{prefix}--main-dock",
            model_id=MODEL_IDS["dock"],
            properties={
                "siteId": f"site:{prefix}",
                "name": "Main Dock",
                "locationType": "dock",
                "status": "available",
                "dockStatus": "available",
                "waterAccessType": "lake",
                "lastUpdatedAt": "2026-03-19T00:00:00Z",
            },
        ),
        TwinSeed(
            twin_id=f"building--{prefix}--main-cottage",
            model_id=MODEL_IDS["building"],
            properties={
                "siteId": f"site:{prefix}",
                "name": "Main Cottage",
                "locationType": "building",
                "status": "available",
                "buildingType": "residential",
                "lastUpdatedAt": "2026-03-19T00:00:00Z",
            },
        ),
        TwinSeed(
            twin_id=f"room--{prefix}--entry",
            model_id=MODEL_IDS["room"],
            properties={
                "siteId": f"site:{prefix}",
                "name": "Entry",
                "locationType": "room",
                "status": "available",
                "roomType": "entry",
                "floorLabel": "main",
                "lastUpdatedAt": "2026-03-19T00:00:00Z",
            },
        ),
        TwinSeed(
            twin_id=f"room--{prefix}--main-floor",
            model_id=MODEL_IDS["room"],
            properties={
                "siteId": f"site:{prefix}",
                "name": "Main Floor",
                "locationType": "room",
                "status": "available",
                "roomType": "hall",
                "floorLabel": "main",
                "lastUpdatedAt": "2026-03-19T00:00:00Z",
            },
        ),
        TwinSeed(
            twin_id=f"room--{prefix}--kitchen",
            model_id=MODEL_IDS["room"],
            properties={
                "siteId": f"site:{prefix}",
                "name": "Kitchen",
                "locationType": "room",
                "status": "available",
                "roomType": "kitchen",
                "floorLabel": "main",
                "lastUpdatedAt": "2026-03-19T00:00:00Z",
            },
        ),
        TwinSeed(
            twin_id=f"room--{prefix}--bedroom",
            model_id=MODEL_IDS["room"],
            properties={
                "siteId": f"site:{prefix}",
                "name": "Bedroom",
                "locationType": "room",
                "status": "available",
                "roomType": "bedroom",
                "floorLabel": "main",
                "lastUpdatedAt": "2026-03-19T00:00:00Z",
            },
        ),
        TwinSeed(
            twin_id="robot--placeholder--carrier-01",
            model_id=MODEL_IDS["robot"],
            properties={
                "robotId": "robot:placeholder:carrier:01",
                "siteId": f"site:{prefix}",
                "name": "Carrier 01",
                "status": "idle",
                "batteryPct": 100.0,
                "connectivity": "unknown",
                "healthStatus": "ok",
                "robotType": "placeholder_carrier",
                "robotCategory": "Wheeled",
                "currentTaskId": "",
                "lastUpdatedAt": "2026-03-19T00:00:00Z",
            },
        ),
        TwinSeed(
            twin_id="boat--placeholder--service-01",
            model_id=MODEL_IDS["boat"],
            properties={
                "boatId": "boat:placeholder:service:01",
                "status": "available",
                "eta": "2026-03-19T00:00:00Z",
                "availability": "available",
                "cargoCapacity": 4,
                "lastUpdatedAt": "2026-03-19T00:00:00Z",
            },
        ),
    ]

    relationships = [
        RelationshipSeed(f"site--{prefix}", "containsLocation", f"zone--{prefix}--landing"),
        RelationshipSeed(f"site--{prefix}", "containsLocation", f"path--{prefix}--landing-to-dock"),
        RelationshipSeed(f"site--{prefix}", "containsLocation", f"dock--{prefix}--main-dock"),
        RelationshipSeed(f"site--{prefix}", "containsLocation", f"building--{prefix}--main-cottage"),
        RelationshipSeed(f"site--{prefix}", "containsRobot", "robot--placeholder--carrier-01"),
        RelationshipSeed(f"site--{prefix}", "containsBoat", "boat--placeholder--service-01"),
        RelationshipSeed(f"building--{prefix}--main-cottage", "containsRoom", f"room--{prefix}--entry"),
        RelationshipSeed(f"building--{prefix}--main-cottage", "containsRoom", f"room--{prefix}--main-floor"),
        RelationshipSeed(f"building--{prefix}--main-cottage", "containsRoom", f"room--{prefix}--kitchen"),
        RelationshipSeed(f"building--{prefix}--main-cottage", "containsRoom", f"room--{prefix}--bedroom"),
        RelationshipSeed(f"zone--{prefix}--landing", "connectedTo", f"path--{prefix}--landing-to-dock"),
        RelationshipSeed(f"path--{prefix}--landing-to-dock", "connectedTo", f"dock--{prefix}--main-dock"),
        RelationshipSeed(f"room--{prefix}--entry", "connectedTo", f"room--{prefix}--main-floor"),
        RelationshipSeed(f"room--{prefix}--main-floor", "connectedTo", f"room--{prefix}--kitchen"),
        RelationshipSeed(f"room--{prefix}--main-floor", "connectedTo", f"room--{prefix}--bedroom"),
        RelationshipSeed("robot--placeholder--carrier-01", "locatedAt", f"zone--{prefix}--landing"),
        RelationshipSeed("boat--placeholder--service-01", "locatedAt", f"dock--{prefix}--main-dock"),
        RelationshipSeed(f"dock--{prefix}--main-dock", "servesBoat", "boat--placeholder--service-01"),
    ]

    return {
        "twins": [seed.to_adt_payload() | {"$dtId": seed.twin_id} for seed in twins],
        "relationships": [seed.to_dict() for seed in relationships],
    }


def provision_placeholder_cottage_graph(
    adapter: TwinGraphProvisioner,
    site_slug: str = "parents-cottage",
) -> dict[str, Any]:
    """Create the placeholder site graph using a compatible adapter."""
    graph = build_placeholder_cottage_graph(site_slug=site_slug)
    twin_results = []
    relationship_results = []

    for twin in graph["twins"]:
        twin_id = twin["$dtId"]
        model_id = twin["$metadata"]["$model"]
        properties = {k: v for k, v in twin.items() if k not in {"$dtId", "$metadata"}}
        twin_results.append(adapter.upsert_twin(twin_id, model_id, properties))

    for relationship in graph["relationships"]:
        relationship_results.append(
            adapter.upsert_relationship(
                relationship["source_id"],
                relationship["relationship_name"],
                relationship["target_id"],
            )
        )

    return {
        "site_slug": site_slug,
        "twin_count": len(twin_results),
        "relationship_count": len(relationship_results),
    }
