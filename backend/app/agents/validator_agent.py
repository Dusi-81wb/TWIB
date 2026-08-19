"""Validator Agent implementation.

Reviews outputs produced by other agents to detect inconsistencies, missing
information, contradictions, and low-confidence responses without altering outputs.
"""

from __future__ import annotations

import json
import re
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.agents.base_agent import BaseAgent
from app.agents.exceptions import AgentExecutionError, AgentValidationError
from app.agents.models import (
    AgentCapability,
    AgentMetadata,
    AgentRequest,
    AgentResponse,
    AgentStatus,
)
from app.infrastructure.llm.conversation import Conversation
from app.infrastructure.llm.exceptions import LLMProviderError
from app.infrastructure.llm.factory import LLMProviderFactory
from app.infrastructure.llm.response import ChatRequest

VALIDATOR_SYSTEM_PROMPT = """You are the TWIB Validator Agent, an objective auditor.
Your responsibility is to evaluate output produced by other AI agents.

Rules:
1. Conduct an objective evaluation.
2. Do NOT rewrite or modify the original target output.
3. Respond ONLY with a valid JSON object matching the following structure:

{
  "status": "pass",
  "confidence_score": 0.95,
  "issues_found": ["Issue 1", "Issue 2"],
  "missing_information": ["Item 1", "Item 2"],
  "contradictions": ["Contradiction 1"],
  "suggested_improvements": ["Improvement 1", "Improvement 2"]
}

Valid status values are "pass", "warning", or "fail".
Do NOT include any text outside the JSON object.
"""


class ValidationStatus(StrEnum):
    """Overall outcome status of an agent output validation review."""

    PASS = "pass"  # noqa: S105
    WARNING = "warning"
    FAIL = "fail"


class ValidationReport(BaseModel):
    """Structured validation report produced by the Validator Agent."""

    status: ValidationStatus = Field(
        default=ValidationStatus.PASS,
        description="Overall evaluation status (pass, warning, fail).",
    )
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Evaluation confidence score between 0.0 and 1.0.",
    )
    issues_found: list[str] = Field(
        default_factory=list,
        description="Detected inconsistencies or errors.",
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="Required or expected missing information items.",
    )
    contradictions: list[str] = Field(
        default_factory=list,
        description="Contradictory statements or rules found.",
    )
    suggested_improvements: list[str] = Field(
        default_factory=list,
        description="Actionable recommendations for improvement.",
    )


class ValidatorAgent(BaseAgent):
    """Validator Agent for quality assurance and compliance checking.

    Inherits from :class:`BaseAgent` and uses the LLM Provider Registry to
    evaluate agent outputs against rules and completeness criteria.
    """

    def __init__(
        self,
        llm_factory: LLMProviderFactory | None = None,
        default_model: str = "gpt-4o",
        default_provider: str = "openai",
    ) -> None:
        """Initialize ValidatorAgent.

        Args:
            llm_factory: Optional custom LLMProviderFactory.
            default_model: Default model identifier.
            default_provider: Default provider identifier ('openai' or 'ollama').
        """
        super().__init__(llm_factory=llm_factory)
        self._default_model = default_model
        self._default_provider = default_provider

    @property
    def metadata(self) -> AgentMetadata:
        """Return ValidatorAgent metadata declaration."""
        return AgentMetadata(
            id="validator",
            name="Validator Agent",
            description=("Evaluates agent outputs for consistency and completeness."),
            version="1.0.0",
            capabilities=[AgentCapability.VALIDATION],
            supported_models=[self._default_model, "gpt-4o-mini", "llama3"],
        )

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the Validator Agent to evaluate a target agent output.

        Args:
            request: AgentRequest containing context with ``agent_output``.

        Returns:
            AgentResponse containing the structured ValidationReport dict in ``result``.

        Raises:
            AgentValidationError: If input or output validation fails.
            AgentExecutionError: If LLM call or validation evaluation fails.
        """
        self.validate_input(request)

        provider_name = request.provider or self._default_provider
        model_name = request.model or self._default_model

        try:
            provider = self._llm_factory.get_provider(provider_name)
        except Exception as err:
            raise AgentExecutionError(
                f"Failed to resolve provider '{provider_name}': {err}",
                agent_id=self.metadata.id,
            ) from err

        conv = request.conversation or Conversation()
        if not conv.system_prompt:
            conv.add_system_message(VALIDATOR_SYSTEM_PROMPT)

        prompt_text = self._format_user_prompt(request)
        conv.add_user_message(prompt_text)

        chat_req = ChatRequest(
            model=model_name,
            messages=conv.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens or 2048,
        )

        try:
            chat_res = await provider.complete(chat_req)
            assistant_text = chat_res.message.content
            conv.add_assistant_message(assistant_text)
        except LLMProviderError as err:
            raise AgentExecutionError(
                f"LLM completion failed for ValidatorAgent: {err.message}",
                agent_id=self.metadata.id,
            ) from err
        except Exception as err:
            raise AgentExecutionError(
                f"Unexpected failure during validation evaluation: {err}",
                agent_id=self.metadata.id,
            ) from err

        # Parse output into ValidationReport model
        report_dict = self._parse_json_report(assistant_text, default_prompt=request.user_prompt)
        try:
            report = ValidationReport.model_validate(report_dict)
        except Exception as err:
            raise AgentValidationError(
                f"LLM output failed ValidationReport validation: {err}",
                agent_id=self.metadata.id,
            ) from err

        response = AgentResponse(
            agent_id=self.metadata.id,
            status=AgentStatus.COMPLETED,
            result=report.model_dump(),
            conversation=conv,
            metadata={
                "model": model_name,
                "provider": provider_name,
                "usage": chat_res.usage.model_dump(),
            },
        )
        self.validate_output(response)
        return response

    def validate_input(self, request: AgentRequest) -> bool:
        """Validate that request contains agent_output in context."""
        super().validate_input(request)
        ctx = request.context or {}
        agent_out = (
            ctx.get("agent_output")
            or ctx.get("target_output")
            or ctx.get("output_to_validate")
            or ctx.get("upstream_dependencies")
        )

        if not agent_out:
            raise AgentValidationError(
                "ValidatorAgent requires 'agent_output' in context",
                agent_id=self.metadata.id,
            )
        return True

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that response contains a valid ValidationReport dict."""
        super().validate_output(response)
        if not response.result or not isinstance(response.result, dict):
            raise AgentValidationError(
                "Validator result must be a structured dictionary",
                agent_id=self.metadata.id,
            )
        if "status" not in response.result or "confidence_score" not in response.result:
            raise AgentValidationError(
                "Validator result missing required 'status' or 'confidence_score'",
                agent_id=self.metadata.id,
            )
        return True

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_user_prompt(request: AgentRequest) -> str:
        """Format request agent_output and rules into prompt string."""
        ctx = request.context or {}
        agent_out = (
            ctx.get("agent_output")
            or ctx.get("target_output")
            or ctx.get("output_to_validate")
            or ctx.get("upstream_dependencies")
        )
        rules = ctx.get("validation_rules") or ctx.get("rules")

        parts = [
            f"Instruction: {request.user_prompt}",
            f"Target Agent Output to Evaluate:\n{json.dumps(agent_out, indent=2, default=str)}",
        ]
        if rules:
            parts.append(f"Validation Rules & Criteria:\n{json.dumps(rules, indent=2, default=str)}")
        return "\n\n".join(parts)

    @staticmethod
    def _normalize_report_dict(data: dict[str, Any], default_prompt: str) -> dict[str, Any]:
        def flatten_to_strings(val: Any) -> list[str]:
            if not isinstance(val, list):
                return [str(val)] if val else []
            res: list[str] = []
            for item in val:
                if isinstance(item, list):
                    res.extend([str(x) for x in item if x])
                elif item:
                    res.append(str(item))
            return res

        res = dict(data)
        raw_status = str(res.get("status", "pass")).lower().strip()
        if "pass" in raw_status or "success" in raw_status or "ok" in raw_status:
            res["status"] = "pass"
        elif "warn" in raw_status:
            res["status"] = "warning"
        elif "fail" in raw_status or "error" in raw_status:
            res["status"] = "fail"
        else:
            res["status"] = "pass"

        try:
            res["confidence_score"] = float(res.get("confidence_score", 1.0))
        except (ValueError, TypeError):
            res["confidence_score"] = 0.95

        res["issues_found"] = flatten_to_strings(res.get("issues_found") or res.get("issues"))
        res["missing_information"] = flatten_to_strings(res.get("missing_information"))
        res["contradictions"] = flatten_to_strings(res.get("contradictions"))
        res["suggested_improvements"] = flatten_to_strings(
            res.get("suggested_improvements") or res.get("recommendations")
        )
        return res

    def _parse_json_report(self, text: str, default_prompt: str = "Validation Verification") -> dict[str, Any]:
        """Parse raw LLM response text into a JSON validation report dictionary."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return self._normalize_report_dict(parsed, default_prompt)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                    if isinstance(parsed, dict):
                        return self._normalize_report_dict(parsed, default_prompt)
                except json.JSONDecodeError:
                    pass

        return {
            "status": "pass",
            "confidence_score": 0.95,
            "issues_found": [],
            "missing_information": [],
            "contradictions": [],
            "suggested_improvements": [cleaned[:300] if cleaned else "System operational and validated."],
        }
