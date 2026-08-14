"""Optimizer Agent implementation.

Refines and improves validated agent outputs for clarity, structure, and brevity
while strictly preserving the original intent and objectives.
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

OPTIMIZER_SYSTEM_PROMPT = """You are the TWIB Optimizer Agent, an expert
optimizer. Your responsibility is to refine validated outputs to improve
clarity, structure, and conciseness while preserving original intent.

Rules:
1. Eliminate redundancy, improve formatting, and optimize organization.
2. Do NOT alter original business requirements or technical objectives.
3. Respond ONLY with a valid JSON object matching the following structure:

{
  "optimized_content": { ... },
  "improvements_applied": ["Applied improvement 1", "Applied improvement 2"],
  "optimization_summary": "Concise summary of optimizations made",
  "confidence_score": 0.98
}

Do NOT include any text outside the JSON object.
"""


class OptimizationResult(BaseModel):
    """Structured optimization result produced by the Optimizer Agent."""

    optimized_content: Any = Field(
        ...,
        description="Refined and optimized content payload.",
    )
    improvements_applied: list[str] = Field(
        default_factory=list,
        description="List of optimization improvements applied.",
    )
    optimization_summary: str = Field(
        default="",
        description="Summary description of optimization changes.",
    )
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the optimization between 0.0 and 1.0.",
    )


class OptimizerAgent(BaseAgent):
    """Optimizer Agent for refining agent outputs.

    Inherits from :class:`BaseAgent` and uses the LLM Provider Registry to
    optimize content structure, clarity, and conciseness.
    """

    def __init__(
        self,
        llm_factory: LLMProviderFactory | None = None,
        default_model: str = "gpt-4o",
        default_provider: str = "openai",
    ) -> None:
        """Initialize OptimizerAgent.

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
        """Return OptimizerAgent metadata declaration."""
        return AgentMetadata(
            id="optimizer",
            name="Optimizer Agent",
            description=("Refines and optimizes validated agent outputs for clarity."),
            version="1.0.0",
            capabilities=[AgentCapability.OPTIMIZATION],
            supported_models=[self._default_model, "gpt-4o-mini", "llama3"],
        )

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the Optimizer Agent to refine target validated output.

        Args:
            request: AgentRequest containing context with ``validated_output``.

        Returns:
            AgentResponse containing the structured OptimizationResult
                dict in ``result``.

        Raises:
            AgentValidationError: If input or output validation fails.
            AgentExecutionError: If LLM call or optimization generation fails.
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
            conv.add_system_message(OPTIMIZER_SYSTEM_PROMPT)

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
                f"LLM completion failed for OptimizerAgent: {err.message}",
                agent_id=self.metadata.id,
            ) from err
        except Exception as err:
            raise AgentExecutionError(
                f"Unexpected failure during optimization generation: {err}",
                agent_id=self.metadata.id,
            ) from err

        opt_dict = self._parse_json_result(assistant_text)
        try:
            opt_res = OptimizationResult.model_validate(opt_dict)
        except Exception as err:
            raise AgentValidationError(
                f"LLM output failed OptimizationResult validation: {err}",
                agent_id=self.metadata.id,
            ) from err

        response = AgentResponse(
            agent_id=self.metadata.id,
            status=AgentStatus.COMPLETED,
            result=opt_res.model_dump(),
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
        """Validate that request contains validated_output in context.

        Args:
            request: Incoming AgentRequest payload.

        Returns:
            True if valid.

        Raises:
            AgentValidationError: If validated_output is missing.
        """
        super().validate_input(request)
        ctx = request.context or {}
        val_out = (
            ctx.get("validated_output")
            or ctx.get("target_output")
            or ctx.get("output_to_optimize")
        )

        if not val_out:
            raise AgentValidationError(
                "OptimizerAgent requires 'validated_output' in context",
                agent_id=self.metadata.id,
            )
        return True

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that response contains a valid OptimizationResult dict.

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
                "Optimizer result must be a structured dictionary",
                agent_id=self.metadata.id,
            )
        if (
            "optimized_content" not in response.result
            or "improvements_applied" not in response.result
        ):
            raise AgentValidationError(
                "Optimizer result missing required output keys",
                agent_id=self.metadata.id,
            )
        return True

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_user_prompt(request: AgentRequest) -> str:
        """Format request validated_output and optimization_goal into prompt string."""
        ctx = request.context or {}
        val_out = (
            ctx.get("validated_output")
            or ctx.get("target_output")
            or ctx.get("output_to_optimize")
        )
        goal = ctx.get("optimization_goal") or request.user_prompt

        parts = [
            f"Optimization Goal: {goal}",
            f"Target Content to Optimize:\n{json.dumps(val_out, indent=2)}",
        ]
        return "\n\n".join(parts)

    def _parse_json_result(self, text: str) -> dict[str, Any]:
        """Parse raw LLM response text into a JSON optimization result dictionary.

        Args:
            text: Response text returned by LLM provider.

        Returns:
            Parsed optimization dictionary.

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
            f"Failed to parse optimization JSON from LLM: {text[:150]}...",
            agent_id=self.metadata.id,
        )
