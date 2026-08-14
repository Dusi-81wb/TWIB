"""Planner Agent implementation.

Converts a user's high-level goal, context, and constraints into a structured,
decomposed execution plan without executing tasks or invoking other agents.
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


PLANNER_SYSTEM_PROMPT = """You are the TWIB Planner Agent, an expert
enterprise system architect.
Your sole responsibility is to analyze a user's business goal, context,
and constraints, and decompose it into a structured execution plan.

Rules:
1. Deconstruct the user goal into logical, step-by-step tasks.
2. Identify assumptions, objectives, risks, and expected deliverable output.
3. Respond ONLY with a valid JSON object matching the following structure:

{
  "goal": "Concise goal statement",
  "assumptions": ["Assumption 1", "Assumption 2"],
  "objectives": ["Objective 1", "Objective 2"],
  "required_tasks": [
    {
      "id": "task_1",
      "name": "Task name",
      "description": "Task description",
      "dependencies": []
    }
  ],
  "task_dependencies": [
    {
      "task_id": "task_2",
      "depends_on": ["task_1"]
    }
  ],
  "risks": ["Risk 1", "Risk 2"],
  "expected_output": "Final deliverable summary"
}

Do NOT include any text outside the JSON object.
"""


class TaskDependency(BaseModel):
    """Dependency link between tasks."""

    task_id: str = Field(..., description="Target task ID.")
    depends_on: list[str] = Field(
        default_factory=list,
        description="Prerequisite task IDs.",
    )


class RequiredTask(BaseModel):
    """Subtask in an execution plan."""

    id: str = Field(..., description="Unique task identifier.")
    name: str = Field(..., description="Short task name.")
    description: str = Field(..., description="Detailed task description.")
    dependencies: list[str] = Field(
        default_factory=list,
        description="IDs of prerequisite tasks.",
    )


class ExecutionPlan(BaseModel):
    """Structured execution plan produced by the Planner Agent."""

    goal: str = Field(..., description="Target goal string.")
    assumptions: list[str] = Field(
        default_factory=list,
        description="List of plan assumptions.",
    )
    objectives: list[str] = Field(
        default_factory=list,
        description="List of core plan objectives.",
    )
    required_tasks: list[RequiredTask] = Field(
        default_factory=list,
        description="Ordered sequence of subtasks.",
    )
    task_dependencies: list[TaskDependency] = Field(
        default_factory=list,
        description="Task dependency relationships.",
    )
    risks: list[str] = Field(
        default_factory=list,
        description="Potential risks and mitigation items.",
    )
    expected_output: str = Field(
        default="",
        description="Expected final deliverable summary.",
    )


class PlannerAgent(BaseAgent):
    """Planner Agent for goal decomposition and execution planning.

    Inherits from :class:`BaseAgent` and uses the LLM Provider Registry to
    generate structured execution plans.
    """

    def __init__(
        self,
        llm_factory: LLMProviderFactory | None = None,
        default_model: str = "gpt-4o",
        default_provider: str = "openai",
    ) -> None:
        """Initialize PlannerAgent.

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
        """Return PlannerAgent metadata declaration."""
        return AgentMetadata(
            id="planner",
            name="Planner Agent",
            description=(
                "Decomposes high-level user goals into structured execution plans."
            ),
            version="1.0.0",
            capabilities=[AgentCapability.PLANNING],
            supported_models=[self._default_model, "gpt-4o-mini", "llama3"],
        )

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the Planner Agent to generate a structured execution plan.

        Args:
            request: AgentRequest containing user_prompt (goal), context, and settings.

        Returns:
            AgentResponse containing the structured ExecutionPlan dict in ``result``.

        Raises:
            AgentValidationError: If input or output validation fails.
            AgentExecutionError: If LLM call or plan generation fails.
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

        # Prepare conversation history
        conv = request.conversation or Conversation()
        if not conv.system_prompt:
            conv.add_system_message(PLANNER_SYSTEM_PROMPT)

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
                f"LLM completion failed for PlannerAgent: {err.message}",
                agent_id=self.metadata.id,
            ) from err
        except Exception as err:
            raise AgentExecutionError(
                f"Unexpected failure during plan generation: {err}",
                agent_id=self.metadata.id,
            ) from err

        # Parse output into ExecutionPlan model
        plan_dict = self._parse_json_plan(assistant_text)
        try:
            plan = ExecutionPlan.model_validate(plan_dict)
        except Exception as err:
            raise AgentValidationError(
                f"LLM output failed ExecutionPlan validation: {err}",
                agent_id=self.metadata.id,
            ) from err

        response = AgentResponse(
            agent_id=self.metadata.id,
            status=AgentStatus.COMPLETED,
            result=plan.model_dump(),
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
        """Validate that request contains a non-empty user prompt / goal.

        Args:
            request: Incoming AgentRequest payload.

        Returns:
            True if valid.

        Raises:
            AgentValidationError: If user prompt is missing or empty.
        """
        super().validate_input(request)
        if len(request.user_prompt.strip()) < 3:
            raise AgentValidationError(
                "Goal prompt is too short to construct an execution plan",
                agent_id=self.metadata.id,
            )
        return True

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that response contains a non-empty ExecutionPlan result.

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
                "Planner result must be a structured dictionary",
                agent_id=self.metadata.id,
            )
        if "goal" not in response.result or "required_tasks" not in response.result:
            raise AgentValidationError(
                "Planner result missing required 'goal' or 'required_tasks' keys",
                agent_id=self.metadata.id,
            )
        return True

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_user_prompt(request: AgentRequest) -> str:
        """Format request user_prompt and context into an LLM prompt string."""
        parts = [f"Goal: {request.user_prompt}"]
        if request.context:
            parts.append(f"Context & Constraints: {json.dumps(request.context)}")
        return "\n\n".join(parts)

    def _parse_json_plan(self, text: str) -> dict[str, Any]:
        """Parse raw LLM response text into a JSON plan dictionary.

        Args:
            text: Response text returned by LLM provider.

        Returns:
            Parsed plan dictionary.

        Raises:
            AgentValidationError: If JSON is malformed or unparseable.
        """
        cleaned = text.strip()
        # Remove markdown code block markers if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)
            cleaned = cleaned.strip()

        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            # Fallback regex search for JSON block
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    logger.warning(
                        "Failed to parse regex match as JSON in PlannerAgent",
                        exc_info=True,
                    )

        raise AgentValidationError(
            f"Failed to parse structured JSON plan from LLM response: {text[:200]}...",
            agent_id=self.metadata.id,
        )
