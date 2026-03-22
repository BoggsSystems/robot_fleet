"""
Dashboard API models for request/response validation.
"""

from .requests import (
    RobotConnectionTest,
    RobotConfig, 
    CalibrationRequest,
    SimulationRequest,
    FleetCreateRequest,
    SiteCreateRequest, 
    ZoneCreateRequest,
    TaskCreateRequest,
    TaskAssignRequest,
    CommandCreateRequest,
    OnboardingUpdateRequest,
    MissionRequest,
    MissionClarificationRequest,
    MissionConfirmRequest,
    MissionControlRequest,
    TaskStatusUpdateRequest,
    MissionApprovalRequest,
)
from .responses import *
from .mobile import *
from .domain import *

__all__ = [
    # Request models
    "RobotConnectionTest",
    "RobotConfig", 
    "CalibrationRequest",
    "SimulationRequest",
    "FleetCreateRequest",
    "SiteCreateRequest", 
    "ZoneCreateRequest",
    "TaskCreateRequest",
    "TaskAssignRequest",
    "CommandCreateRequest",
    "OnboardingUpdateRequest",
    "MissionRequest",
    "MissionClarificationRequest",
    "MissionConfirmRequest",
    "MissionControlRequest",
    "TaskStatusUpdateRequest",
    "MissionApprovalRequest",
    
    # Response models
    "FleetStatusResponse",
    "TaskResponse",
    "MissionResponse",
    "BrainResourcesResponse",
    
    # Mobile models
    "MobileMissionQuestionResponse",
    "MissionEventResponse", 
    "MobileMissionResponse",
    "MissionPreviewPayloadResponse",
    "MobileMissionPreviewEnvelope",
    "MobileMissionDispatchEnvelope",
    "MobileMissionListEnvelope",
    "MobileMissionDetailEnvelope",
]
