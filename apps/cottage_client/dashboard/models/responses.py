"""
Response models for API endpoint responses.
"""

from typing import Any, Optional
from pydantic import BaseModel


class FleetStatusResponse(BaseModel):
    robots: list[dict]
    active_tasks: list[dict]
    completed_tasks: list[dict]
    onboarding_mode: bool
    registry: dict


class TaskResponse(BaseModel):
    task: dict


class MissionResponse(BaseModel):
    mission: dict


class BrainResourcesResponse(BaseModel):
    resources: dict


class RobotConnectionResponse(BaseModel):
    success: bool
    model: str
    serial: str
    firmware: str
    battery: int
    message: str


class RobotRegistrationResponse(BaseModel):
    success: bool
    message: str
    robot: dict
    onboarding: dict


class CalibrationResponse(BaseModel):
    success: bool
    step: str
    message: str
    onboarding: dict


class SimulationResponse(BaseModel):
    success: bool
    scenario: str
    message: str
    metrics: dict


class TaskAssignmentResponse(BaseModel):
    task: dict


class TaskExecutionResponse(BaseModel):
    task: dict


class CommandResponse(BaseModel):
    command: dict


class CommandDispatchResponse(BaseModel):
    command: dict
