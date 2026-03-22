"""
Domain models for core business logic.
"""

from typing import Any, Optional
from pydantic import BaseModel


class RobotProfile(BaseModel):
    robot_id: str
    name: str
    robot_type: str
    robot_category: str
    capabilities: list[str]
    ip_address: str
    network_interface: str
    site_id: str
    zone_id: str
    model: str
    serial: str
    firmware: str
    vendor: str
    status: str = "idle"
    battery_level: Optional[float] = None
    last_seen: Optional[str] = None


class TaskRecord(BaseModel):
    task_id: str
    task_type: str
    status: str
    robot_id: Optional[str] = None
    zone_id: Optional[str] = None
    spec: dict
    result: Optional[dict] = None
    created_at: str
    updated_at: str
    assigned_at: Optional[str] = None
    completed_at: Optional[str] = None


class MissionSession(BaseModel):
    mission_id: str
    request_text: str
    requested_by: str
    status: str
    preview: Optional[dict] = None
    question: Optional[dict] = None
    task_ids: list[str] = []
    metadata: dict = {}
    created_at: str
    updated_at: str


class FleetOverview(BaseModel):
    fleets: list[dict]
    sites: list[dict]
    zones: list[dict]
    robots: list[dict]
    active_tasks: list[dict]
    completed_tasks: list[dict]


class ResourceAssessment(BaseModel):
    available_robots: list[RobotProfile]
    total_robots: int
    idle_robots: int
    busy_robots: int
    offline_robots: int
    capabilities_by_type: dict[str, list[str]]
    zones_with_robots: list[str]


class MissionPlan(BaseModel):
    mission_id: str
    mission_type: str
    request_text: str
    tasks: list[dict]
    assignments: list[dict]
    explanation: Optional[dict] = None
    status: str


class TaskAssignment(BaseModel):
    task_id: str
    robot_id: str
    assignment_score: float
    rationale: str
    fallback_robot_ids: list[str] = []
    assigned_at: str
