"""
Mobile-specific models for iOS app integration.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class MobileMissionQuestionResponse(BaseModel):
    mission_id: str
    prompt: str
    field_name: str
    reason: str


class MissionEventResponse(BaseModel):
    id: str
    time: str
    message: str
    tone: str
    task_id: Optional[str] = None
    status: Optional[str] = None


class MobileMissionResponse(BaseModel):
    missionId: str
    title: str
    requestText: str
    status: str
    missionType: str
    from_: Optional[str] = Field(default=None, alias="from")
    to: Optional[str] = None
    assignedRobotId: Optional[str] = None
    taskCount: int
    taskIds: list[str]
    clarificationRequired: bool
    clarificationQuestion: Optional[MobileMissionQuestionResponse] = None
    summary: str
    currentStep: Optional[str] = None
    currentTaskId: Optional[str] = None
    completedSteps: int = 0
    totalSteps: int = 0
    fallbackAvailable: bool = False
    fallbackRobotIds: list[str] = []
    blockedReason: Optional[str] = None
    createdAt: str
    updatedAt: str

    model_config = {"populate_by_name": True}


class MissionPreviewPayloadResponse(BaseModel):
    status: str
    intent_provider: Optional[str] = None
    question: Optional[dict[str, Any]] = None
    intent: Optional[dict[str, Any]] = None
    resources: Optional[dict[str, Any]] = None
    plan: Optional[dict[str, Any]] = None
    explanation: Optional[dict[str, Any]] = None


class MobileMissionPreviewEnvelope(BaseModel):
    mission: MobileMissionResponse
    preview: MissionPreviewPayloadResponse


class MobileMissionDispatchEnvelope(BaseModel):
    mission: MobileMissionResponse
    dispatch: Optional[dict[str, Any]] = None


class MobileMissionListEnvelope(BaseModel):
    missions: list[MobileMissionResponse]


class MobileMissionDetailEnvelope(BaseModel):
    mission: MobileMissionResponse
    preview: MissionPreviewPayloadResponse
    events: list[MissionEventResponse] = []
