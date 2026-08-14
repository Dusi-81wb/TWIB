"""Analyst Agent implementation.

Transforms planner execution plans and research reports into structured,
categorized business, functional, and non-functional requirements.
"""

from __future__ import annotations

import json
import re
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
from app.core.logging import get_logger
from app.infrastructure.llm.conversation import Conversation
from app.infrastructure.llm.exceptions import LLMProviderError
from app.infrastructure.llm.factory import LLMProviderFactory
from app.infrastructure.llm.response import ChatRequest

logger = get_logger(__name__)

ANALYST_SYSTEM_PROMPT = """You are the TWIB Analyst Agent, an expert analyst.
Your responsibility is to synthesize planning and research outputs into clear,
categorized requirements.

Rules:
1. Extract and categorize requirements cleanly without designing solutions or workflows.
2. Identify ambiguity, constraints, risks, and success criteria.
3. Respond ONLY with a valid JSON object matching the following structure:

{
  "business_requirements": ["Requirement 1", "Requirement 2"],
  "functional_requirements": ["Requirement 1", "Requirement 2"],
  "non_functional_requirements": ["Requirement 1", "Requirement 2"],
  "constraints": ["Constraint 1", "Constraint 2"],
  "assumptions": ["Assumption 1", "Assumption 2"],
  "risks": ["Risk 1", "Risk 2"],
  "success_criteria": ["Criteria 1", "Criteria 2"]
}

Do NOT include any text outside the JSON object.
"""


class RequirementsAnalysis(BaseModel):
    """Structured requirements analysis produced by the Analyst Agent."""

    business_requirements: list[str] = Field(
        default_factory=list,
        description="Business requirements list.",
    )
    functional_requirements: list[str] = Field(
        default_factory=list,
        description="Functional requirements list.",
    )
    non_functional_requirements: list[str] = Field(
        default_factory=list,
        description="Non-functional requirements list.",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Technical and operational constraints.",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Analysis assumptions.",
    )
    risks: list[str] = Field(
        default_factory=list,
        description="Identified risks.",
    )
    success_criteria: list[str] = Field(
        default_factory=list,
        description="Measurable success criteria.",
    )


class AnalystAgent(BaseAgent):
    """Analyst Agent for requirements synthesis and analysis.

    Inherits from :class:`BaseAgent` and uses the LLM Provider Registry to
    generate structured requirement specifications.
    """

    def __init__(
        self,
        llm_factory: LLMProviderFactory | None = None,
        default_model: str = "gpt-4o",
        default_provider: str = "openai",
    ) -> None:
        """Initialize AnalystAgent.

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
        """Return AnalystAgent metadata declaration."""
        return AgentMetadata(
            id="analyst",
            name="Analyst Agent",
            description=("Transforms planning and research outputs into requirements."),
            version="1.0.0",
            capabilities=[AgentCapability.VALIDATION],
            supported_models=[self._default_model, "gpt-4o-mini", "llama3"],
        )

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the Analyst Agent to generate a requirements specification.

        Args:
            request: AgentRequest containing context with ``planning_result``
                and ``research_result``.

        Returns:
            AgentResponse containing the structured RequirementsAnalysis
                dict in ``result``.

        Raises:
            AgentValidationError: If input or output validation fails.
            AgentExecutionError: If LLM call or analysis generation fails.
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
            conv.add_system_message(ANALYST_SYSTEM_PROMPT)

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
                f"LLM completion failed for AnalystAgent: {err.message}",
                agent_id=self.metadata.id,
            ) from err
        except Exception as err:
            raise AgentExecutionError(
                f"Unexpected failure during requirements analysis: {err}",
                agent_id=self.metadata.id,
            ) from err

        analysis_dict = self._parse_json_analysis(assistant_text)
        try:
            analysis = RequirementsAnalysis.model_validate(analysis_dict)
        except Exception as err:
            raise AgentValidationError(
                f"LLM output failed RequirementsAnalysis validation: {err}",
                agent_id=self.metadata.id,
            ) from err

        response = AgentResponse(
            agent_id=self.metadata.id,
            status=AgentStatus.COMPLETED,
            result=analysis.model_dump(),
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
        """Validate that request contains planning and research results in context.

        Args:
            request: Incoming AgentRequest payload.

        Returns:
            True if valid.

        Raises:
            AgentValidationError: If planning or research results are missing.
        """
        super().validate_input(request)
        ctx = request.context or {}
        planning_res = ctx.get("planning_result") or ctx.get("plan")
        research_res = ctx.get("research_result") or ctx.get("research")

        if not planning_res:
            raise AgentValidationError(
                "AnalystAgent requires 'planning_result' in context",
                agent_id=self.metadata.id,
            )
        if not research_res:
            raise AgentValidationError(
                "AnalystAgent requires 'research_result' in context",
                agent_id=self.metadata.id,
            )
        return True

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that response contains a non-empty RequirementsAnalysis dict.

        Args:
            response: Outgoing AgentResponse payload.

        Returns:
            True if valid.

        Raises:
            AgentValidationError: If result is missing or incomplete.
        """
        super().validate_output(response)
        if not response.result or not isinstance(response.result, dict):
            raise AgentValidationError(
                "Analyst result must be a structured dictionary",
                agent_id=self.metadata.id,
            )
        if (
            "functional_requirements" not in response.result
            or "business_requirements" not in response.result
        ):
            raise AgentValidationError(
                "Analyst result missing required requirements keys",
                agent_id=self.metadata.id,
            )
        return True

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_user_prompt(request: AgentRequest) -> str:
        """Format request planning and research context into prompt string."""
        ctx = request.context or {}
        planning = ctx.get("planning_result") or ctx.get("plan")
        research = ctx.get("research_result") or ctx.get("research")

        parts = [
            f"Instruction: {request.user_prompt}",
            f"Planning Result:\n{json.dumps(planning, indent=2)}",
            f"Research Result:\n{json.dumps(research, indent=2)}",
        ]
        return "\n\n".join(parts)

    def _parse_json_analysis(self, text: str) -> dict[str, Any]:
        """Parse raw LLM response text into a JSON requirements dictionary.

        Args:
            text: Response text returned by LLM provider.

        Returns:
            Parsed requirements dictionary.

        Raises:
            AgentValidationError: If JSON is malformed or unparseable.
        """
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError as err:

                    logger.warning(
                        "Failed to parse JSON from regex match", error=str(err)
                    )

        raise AgentValidationError(
            f"Failed to parse requirements JSON from LLM: {text[:150]}...",
            agent_id=self.metadata.id,
        )
