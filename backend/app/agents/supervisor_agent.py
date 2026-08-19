"""Supervisor Agent implementation.

Orchestrates and coordinates execution across all specialized agents
(Planner, Research, Analyst, Architect, Validator, Optimizer, Documentation)
in a logical sequential pipeline with error handling and result aggregation.
"""

from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, Field

from app.agents.analyst_agent import AnalystAgent
from app.agents.architect_agent import ArchitectAgent
from app.agents.base_agent import BaseAgent
from app.agents.documentation_agent import DocumentationAgent
from app.agents.exceptions import AgentError, AgentValidationError
from app.agents.models import (
    AgentCapability,
    AgentMetadata,
    AgentRequest,
    AgentResponse,
    AgentStatus,
)
from app.agents.optimizer_agent import OptimizerAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.validator_agent import ValidatorAgent
from app.infrastructure.llm.factory import LLMProviderFactory

DEFAULT_PIPELINE: list[str] = [
    "planner",
    "research",
    "analyst",
    "architect",
    "validator",
    "optimizer",
    "documentation",
]


class AgentExecutionStep(BaseModel):
    """Execution status and result for an individual agent in the pipeline."""

    agent_id: str = Field(..., description="ID of the executed agent.")
    status: AgentStatus = Field(..., description="Execution status.")
    duration_seconds: float = Field(default=0.0, description="Step execution time.")
    result: Any = Field(default=None, description="Agent execution output result.")
    error: str | None = Field(default=None, description="Error message if step failed.")


class SupervisorResult(BaseModel):
    """Aggregated execution report produced by the Supervisor Agent."""

    objective: str = Field(..., description="User prompt or execution objective.")
    execution_pipeline: list[str] = Field(
        default_factory=list,
        description="Planned list of agent IDs in execution order.",
    )
    executed_steps: list[AgentExecutionStep] = Field(
        default_factory=list,
        description="Executed agent step records.",
    )
    final_result: Any = Field(
        default=None,
        description="Output result of the final successfully executed agent.",
    )
    summary: str = Field(
        default="",
        description="Executive summary of the coordinated pipeline execution.",
    )
    total_duration_seconds: float = Field(
        default=0.0,
        description="Total duration of the pipeline execution in seconds.",
    )


class SupervisorAgent(BaseAgent):
    """Supervisor Agent for agent orchestration and workflow coordination.

    Inherits from :class:`BaseAgent` and manages execution sequence, context passing,
    and exception boundaries across all specialized TWIB agents.
    """

    def __init__(
        self,
        llm_factory: LLMProviderFactory | None = None,
        default_model: str = "gpt-4o",
        default_provider: str = "openai",
        agent_registry: dict[str, BaseAgent] | None = None,
    ) -> None:
        """Initialize SupervisorAgent.

        Args:
            llm_factory: Optional custom LLMProviderFactory.
            default_model: Default model identifier.
            default_provider: Default provider identifier ('openai' or 'ollama').
            agent_registry: Optional mapping of agent_id -> BaseAgent instances.
        """
        super().__init__(llm_factory=llm_factory)
        self._default_model = default_model
        self._default_provider = default_provider

        # Initialize or register child agent instances
        if agent_registry is not None:
            self._agents = agent_registry
        else:
            self._agents = {
                "planner": PlannerAgent(llm_factory=self._llm_factory),
                "research": ResearchAgent(llm_factory=self._llm_factory),
                "analyst": AnalystAgent(llm_factory=self._llm_factory),
                "architect": ArchitectAgent(llm_factory=self._llm_factory),
                "validator": ValidatorAgent(llm_factory=self._llm_factory),
                "optimizer": OptimizerAgent(llm_factory=self._llm_factory),
                "documentation": DocumentationAgent(llm_factory=self._llm_factory),
            }

    @property
    def metadata(self) -> AgentMetadata:
        """Return SupervisorAgent metadata declaration."""
        return AgentMetadata(
            id="supervisor",
            name="Supervisor Agent",
            description=(
                "Orchestrates multi-agent pipelines and coordinates execution."
            ),
            version="1.0.0",
            capabilities=[AgentCapability.SUPERVISION],
            supported_models=[self._default_model, "gpt-4o-mini", "llama3"],
        )

    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the Supervisor Agent pipeline.

        Args:
            request: AgentRequest containing user prompt and optional pipeline context.

        Returns:
            AgentResponse containing the structured SupervisorResult dict in ``result``.

        Raises:
            AgentValidationError: If input validation fails.
            AgentExecutionError: If supervisor setup fails catastrophically.
        """
        self.validate_input(request)

        ctx = dict(request.context or {})
        pipeline = ctx.get("agent_pipeline") or DEFAULT_PIPELINE
        if not isinstance(pipeline, list):
            pipeline = DEFAULT_PIPELINE

        provider_name = request.provider or self._default_provider
        model_name = request.model or self._default_model

        pipeline_start_time = time.monotonic()
        executed_steps: list[AgentExecutionStep] = []
        last_result: Any = None
        pipeline_status = AgentStatus.COMPLETED
        failure_error_msg: str | None = None

        for agent_id in pipeline:
            if agent_id not in self._agents:
                # Skip unknown agent IDs with error recording
                step_rec = AgentExecutionStep(
                    agent_id=str(agent_id),
                    status=AgentStatus.FAILED,
                    error=f"Agent '{agent_id}' not found in supervisor registry",
                )
                executed_steps.append(step_rec)
                pipeline_status = AgentStatus.FAILED
                break

            agent = self._agents[agent_id]
            step_start = time.monotonic()

            # Format contextual request payload for the specific step
            step_request = AgentRequest(
                agent_id=agent_id,
                user_prompt=request.user_prompt,
                context=dict(ctx),
                provider=provider_name,
                model=model_name,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            try:
                step_res = await agent.execute(step_request)
                step_duration = round(time.monotonic() - step_start, 3)

                step_rec = AgentExecutionStep(
                    agent_id=agent_id,
                    status=step_res.status,
                    duration_seconds=step_duration,
                    result=step_res.result,
                )
                executed_steps.append(step_rec)
                last_result = step_res.result

                # Propagate contextual state forward for subsequent agents in chain
                self._update_shared_context(ctx, agent_id, step_res.result)

            except AgentError as err:
                step_duration = round(time.monotonic() - step_start, 3)
                failure_error_msg = err.message
                step_rec = AgentExecutionStep(
                    agent_id=agent_id,
                    status=AgentStatus.FAILED,
                    duration_seconds=step_duration,
                    error=failure_error_msg,
                )
                executed_steps.append(step_rec)
                pipeline_status = AgentStatus.FAILED
                break
            except Exception as err:
                step_duration = round(time.monotonic() - step_start, 3)
                failure_error_msg = f"Unexpected failure in agent '{agent_id}': {err}"
                step_rec = AgentExecutionStep(
                    agent_id=agent_id,
                    status=AgentStatus.FAILED,
                    duration_seconds=step_duration,
                    error=failure_error_msg,
                )
                executed_steps.append(step_rec)
                pipeline_status = AgentStatus.FAILED
                break

        total_duration = round(time.monotonic() - pipeline_start_time, 3)
        halt_msg = (
            f"Pipeline halted at step '{executed_steps[-1].agent_id}' due to error."
        )
        summary = (
            f"Successfully executed {len(executed_steps)} agents in pipeline."
            if pipeline_status == AgentStatus.COMPLETED
            else halt_msg
        )

        sup_result = SupervisorResult(
            objective=request.user_prompt,
            execution_pipeline=[str(a) for a in pipeline],
            executed_steps=executed_steps,
            final_result=last_result,
            summary=summary,
            total_duration_seconds=total_duration,
        )

        response = AgentResponse(
            agent_id=self.metadata.id,
            status=pipeline_status,
            result=sup_result.model_dump(),
            error=failure_error_msg,
            metadata={
                "model": model_name,
                "provider": provider_name,
                "steps_count": len(executed_steps),
            },
        )
        self.validate_output(response)
        return response

    def validate_input(self, request: AgentRequest) -> bool:
        """Validate that request contains a non-empty user_prompt objective.

        Args:
            request: Incoming AgentRequest payload.

        Returns:
            True if valid.

        Raises:
            AgentValidationError: If prompt is empty.
        """
        super().validate_input(request)
        if not request.user_prompt or not request.user_prompt.strip():
            raise AgentValidationError(
                "SupervisorAgent requires a non-empty 'user_prompt'",
                agent_id=self.metadata.id,
            )
        return True

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate that response contains a valid SupervisorResult dict.

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
                "Supervisor result must be a structured dictionary",
                agent_id=self.metadata.id,
            )
        if "executed_steps" not in response.result:
            raise AgentValidationError(
                "Supervisor result missing required 'executed_steps'",
                agent_id=self.metadata.id,
            )
        return True

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _update_shared_context(
        ctx: dict[str, Any], agent_id: str, step_result: Any
    ) -> None:
        """Propagate output forward into shared pipeline context."""
        if agent_id == "planner":
            ctx["planning_result"] = step_result
            ctx["execution_plan"] = step_result
        elif agent_id == "research":
            ctx["research_result"] = step_result
        elif agent_id == "analyst":
            ctx["analysis_result"] = step_result
            ctx["requirements"] = step_result
        elif agent_id == "architect":
            ctx["architecture_result"] = step_result
            ctx["agent_output"] = step_result
            ctx["target_output"] = step_result
        elif agent_id == "validator":
            ctx["validation_result"] = step_result
            ctx["validated_output"] = step_result
        elif agent_id == "optimizer":
            ctx["optimized_result"] = step_result
            ctx["optimized_output"] = step_result
            ctx["input_content"] = step_result
        elif agent_id == "documentation":
            ctx["documentation_result"] = step_result
