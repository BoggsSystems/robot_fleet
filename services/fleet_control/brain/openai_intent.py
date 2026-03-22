"""
Optional OpenAI-backed mission intent parsing.

This adapter keeps the LLM bounded to intent translation and clarification.
Policy validation, planning, and dispatch remain deterministic. If the OpenAI
SDK or credentials are unavailable, callers should fall back to the local
parser.
"""

from __future__ import annotations

import json
import os
from typing import Any, Iterable
from uuid import uuid4

from .domain import ClarificationQuestion, MissionConstraint, MissionIntent

_sdk_available = False
OpenAI = None
AzureOpenAI = None

try:
    from openai import AzureOpenAI as _AzureOpenAI
    from openai import OpenAI as _OpenAI

    OpenAI = _OpenAI
    AzureOpenAI = _AzureOpenAI
    _sdk_available = True
except ImportError:
    pass


SYSTEM_PROMPT = """You are an intent parser for a household robot fleet.
Return only valid JSON.

Schema:
{
  "mission_type": "cargo_transfer|inspection|general_assistance",
  "objective": "string",
  "source_zone": "string|null",
  "destination_zone": "string|null",
  "cargo_type": "string|null",
  "priority": "low|normal|high|urgent",
  "required_capabilities": ["string"],
  "constraints": [{"key": "string", "value": any, "severity": "info|warn|error"}],
  "human_confirmation_required": true,
  "clarification_needed": false,
  "clarification_prompt": "string|null",
  "clarification_field": "string|null"
}

Only use zones explicitly mentioned in the request or in the known_zones list.
If a required source or destination is missing or ambiguous, set clarification_needed=true.
Do not issue robot commands. Do not invent capabilities that are unrelated to the request.
"""


class OpenAIIntentService:
    """OpenAI/Azure OpenAI-backed intent parser with deterministic fallback."""

    def __init__(self, known_zones: Iterable[str], fallback: Any):
        self._known_zones = tuple(sorted(set(known_zones)))
        self._fallback = fallback
        self._provider = None
        self._model = None
        self._client = self._build_client()

    @property
    def enabled(self) -> bool:
        return self._client is not None and self._model is not None

    @property
    def provider_label(self) -> str:
        return self._provider or "local-rule-parser"

    def parse_request(
        self,
        request_text: str,
        *,
        requested_by: str,
        context: dict | None = None,
    ) -> MissionIntent | ClarificationQuestion:
        if not self.enabled:
            return self._fallback.parse_request(request_text, requested_by=requested_by, context=context)

        try:
            response = self._client.responses.create(
                model=self._model,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "request_text": request_text,
                                "requested_by": requested_by,
                                "known_zones": list(self._known_zones),
                                "context": context or {},
                            }
                        ),
                    },
                ],
            )
            payload = json.loads(response.output_text)
        except Exception:
            return self._fallback.parse_request(
                request_text,
                requested_by=requested_by,
                context={**(context or {}), "intent_provider": "local-fallback"},
            )

        mission_id = f"msn-{uuid4().hex[:8]}"
        if payload.get("clarification_needed"):
            return ClarificationQuestion(
                question_id=str(uuid4()),
                mission_id=mission_id,
                prompt=payload.get("clarification_prompt") or "Can you clarify the mission request?",
                field_name=payload.get("clarification_field") or "objective",
                reason="LLM parser marked the request as ambiguous.",
            )

        constraints = tuple(
            MissionConstraint(
                key=str(item.get("key", "constraint")),
                value=item.get("value"),
                severity=_normalize_severity(item.get("severity")),
            )
            for item in payload.get("constraints", [])
            if isinstance(item, dict)
        )

        merged_metadata = dict(context or {})
        merged_metadata["intent_provider"] = self.provider_label
        merged_metadata["llm_model"] = self._model

        return MissionIntent(
            mission_id=mission_id,
            mission_type=str(payload.get("mission_type") or "general_assistance"),
            objective=str(payload.get("objective") or request_text.strip()),
            requested_by=requested_by,
            source_zone=_normalize_optional_string(payload.get("source_zone")),
            destination_zone=_normalize_optional_string(payload.get("destination_zone")),
            cargo_type=_normalize_optional_string(payload.get("cargo_type")),
            priority=_normalize_priority(payload.get("priority")),
            required_capabilities=tuple(
                str(item).strip()
                for item in payload.get("required_capabilities", [])
                if str(item).strip()
            ),
            constraints=constraints,
            human_confirmation_required=bool(payload.get("human_confirmation_required", False)),
            metadata=merged_metadata,
        )

    def _build_client(self):
        if not _sdk_available:
            return None

        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        if azure_endpoint and azure_api_key and azure_deployment and AzureOpenAI is not None:
            self._provider = "azure-openai"
            self._model = azure_deployment
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
            return AzureOpenAI(
                api_key=azure_api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint,
            )

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key and OpenAI is not None:
            self._provider = "openai"
            self._model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
            return OpenAI(api_key=openai_api_key)

        return None


def _normalize_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_priority(value: Any) -> str:
    text = str(value or "normal").strip().lower()
    if text in {"low", "normal", "high", "urgent"}:
        return text
    return "normal"


def _normalize_severity(value: Any) -> str:
    text = str(value or "info").strip().lower()
    if text in {"info", "warn", "error"}:
        return text
    return "info"
