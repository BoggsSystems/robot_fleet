"""
Optional OpenAI-backed mission proposal enrichment.

This adapter is bounded to proposal generation only. It can refine assumptions,
warnings, and operator-facing rationale, but it does not authorize execution.
If the model or credentials are unavailable, callers should fall back to the
deterministic local proposal service.
"""

from __future__ import annotations

import json
import os
from typing import Any

from .openai_intent import AzureOpenAI, OpenAI, _sdk_available


SYSTEM_PROMPT = """You are a mission proposal generator for a household robot fleet.
Return only valid JSON.

Schema:
{
  "plan_summary": "string",
  "assumptions": ["string"],
  "warnings": ["string"],
  "operator_notes": ["string"]
}

You are enriching an already-generated deterministic candidate plan. Do not invent
new robots, zones, route steps, or task steps. Do not issue commands. Keep assumptions and
warnings concise and operational. Prefer references to the provided site graph context
and route labels rather than generic wording.
"""


class OpenAIProposalService:
    """Optional proposal enricher backed by OpenAI/Azure OpenAI."""

    def __init__(self, fallback: Any):
        self._fallback = fallback
        self._provider = None
        self._model = None
        self._client = self._build_client()

    @property
    def enabled(self) -> bool:
        return self._client is not None and self._model is not None

    @property
    def provider_label(self) -> str:
        return self._provider or "local-proposal"

    def build_proposal(self, intent: Any, resources: Any) -> dict[str, Any]:
        proposal = self._fallback.build_proposal(intent, resources)
        if not self.enabled:
            return proposal

        try:
            response = self._client.responses.create(
                model=self._model,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "intent": intent.to_dict(),
                                "resources": resources.to_dict(),
                                "candidate_plan": proposal,
                                "site_context": {
                                    "plan_summary": proposal.get("plan_summary"),
                                    "candidate_steps": [
                                        {
                                            "summary": step.get("summary"),
                                            "route_labels": step.get("route_labels", []),
                                        }
                                        for step in proposal.get("candidate_steps", [])
                                    ],
                                },
                            }
                        ),
                    },
                ],
            )
            payload = json.loads(response.output_text)
        except Exception:
            proposal["provider"] = "local-proposal-fallback"
            return proposal

        proposal["provider"] = self.provider_label
        if isinstance(payload.get("plan_summary"), str) and payload["plan_summary"].strip():
            proposal["plan_summary"] = payload["plan_summary"].strip()
        proposal["assumptions"] = _merge_unique(proposal.get("assumptions", []), payload.get("assumptions", []))
        proposal["warnings"] = _merge_unique(proposal.get("warnings", []), payload.get("warnings", []))
        proposal["operator_notes"] = _merge_unique(proposal.get("operator_notes", []), payload.get("operator_notes", []))
        return proposal

    def _build_client(self):
        if not _sdk_available:
            return None

        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        if azure_endpoint and azure_api_key and azure_deployment and AzureOpenAI is not None:
            self._provider = "azure-openai-proposal"
            self._model = azure_deployment
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
            return AzureOpenAI(
                api_key=azure_api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint,
            )

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key and OpenAI is not None:
            self._provider = "openai-proposal"
            self._model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
            return OpenAI(api_key=openai_api_key)

        return None


def _merge_unique(existing: list[str], incoming: Any) -> list[str]:
    values = [str(item).strip() for item in incoming or [] if str(item).strip()]
    merged = list(existing)
    for value in values:
        if value not in merged:
            merged.append(value)
    return merged
