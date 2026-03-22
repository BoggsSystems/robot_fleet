"""
Optional OpenAI-backed replan enrichment.

This adapter is bounded to operator-facing replan explanation only. It does not
change the chosen action, route, or robot candidates; it can only refine the
summary and review notes around a deterministic replan proposal.
"""

from __future__ import annotations

import json
import os
from typing import Any

from .openai_intent import AzureOpenAI, OpenAI, _sdk_available


SYSTEM_PROMPT = """You are a mission replan explainer for a household robot fleet.
Return only valid JSON.

Schema:
{
  "review_summary": "string",
  "operator_notes": ["string"],
  "warnings": ["string"]
}

You are enriching an already-generated deterministic replan proposal. Do not
invent new actions, robots, routes, zones, or commands. Keep the language short,
operational, and suitable for a human approval step.
"""


class OpenAIReplanService:
    def __init__(self):
        self._provider = None
        self._model = None
        self._client = self._build_client()

    @property
    def enabled(self) -> bool:
        return self._client is not None and self._model is not None

    @property
    def provider_label(self) -> str:
        return self._provider or "local-replan"

    def enrich(self, replan: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            replan["provider"] = replan.get("provider") or "local-replan"
            return replan

        try:
            response = self._client.responses.create(
                model=self._model,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "replan": replan,
                                "context": context,
                            }
                        ),
                    },
                ],
            )
            payload = json.loads(response.output_text)
        except Exception:
            replan["provider"] = replan.get("provider") or "local-replan-fallback"
            return replan

        replan["provider"] = self.provider_label
        if isinstance(payload.get("review_summary"), str) and payload["review_summary"].strip():
            replan["reviewSummary"] = payload["review_summary"].strip()
        replan["operatorNotes"] = _merge_unique(replan.get("operatorNotes", []), payload.get("operator_notes", []))
        replan["warnings"] = _merge_unique(replan.get("warnings", []), payload.get("warnings", []))
        return replan

    def _build_client(self):
        if not _sdk_available:
            return None

        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        if azure_endpoint and azure_api_key and azure_deployment and AzureOpenAI is not None:
            self._provider = "azure-openai-replan"
            self._model = azure_deployment
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview")
            return AzureOpenAI(
                api_key=azure_api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint,
            )

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key and OpenAI is not None:
            self._provider = "openai-replan"
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
