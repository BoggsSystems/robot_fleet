"""
Request models for API endpoint validation.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class RobotConnectionTest(BaseModel):
    ip: str
    interface: str = "lo0"


class RobotConfig(BaseModel):
    robotId: str
    name: str
    ipAddress: str
    networkInterface: str
    zone: str
    subZone: str
    capabilities: list
    model: str = "Unitree R1"
    serial: str = ""
    firmware: str = ""
    robotType: str = "unitree_r1"
    robotCategory: str = "Humanoid"
    vendor: str = "unitree_sdk2"


class CalibrationRequest(BaseModel):
    robotId: str
    step: str
    ip: str


class SimulationRequest(BaseModel):
    robotId: str
    scenario: str


class FleetCreateRequest(BaseModel):
    fleetId: str
    name: str
    status: str = "active"


class SiteCreateRequest(BaseModel):
    siteId: str
    name: str
    status: str = "active"


class ZoneCreateRequest(BaseModel):
    zoneId: str
    siteId: str
    name: str
    zoneType: str = "operational"
    parentZoneId: Optional[str] = None


class TaskCreateRequest(BaseModel):
    taskType: str
    spec: dict
    robotId: Optional[str] = None
    zoneId: Optional[str] = None


class TaskAssignRequest(BaseModel):
    robotId: str


class CommandCreateRequest(BaseModel):
    robotId: str
    commandType: str
    parameters: dict
    issuedBy: str = "operator@local"


class OnboardingUpdateRequest(BaseModel):
    stage: str
    status: str
    details: dict = {}


class MissionRequest(BaseModel):
    requestText: str
    requestedBy: str = "operator@local"
    context: dict = {}


class MissionClarificationRequest(BaseModel):
    answer: str


class MissionConfirmRequest(BaseModel):
    confirmedBy: str = "operator@local"


class MissionControlRequest(BaseModel):
    requestedBy: str = "operator@local"


class TaskStatusUpdateRequest(BaseModel):
    status: str
    result: dict = {}


class MissionApprovalRequest(BaseModel):
    approvedBy: str = "operator@local"
