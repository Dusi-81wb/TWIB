"""Abstract BaseAgent interface for the Agent Core framework.

Every AI Agent (Planner, Researcher, Architect, Validator, Optimizer, etc.)
inherits from :class:`BaseAgent`. It defines the contract for input/output
validation, execution, health checking, and metadata declaration.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.agents.exceptions import AgentValidationError
from app.agents.models import AgentMetadata, AgentRequest, AgentResponse, AgentStatus
from app.infrastructure.llm.factory import LLMProviderFactory


class BaseAgent(ABC):
    """Abstract base class for all AI Agents in TWIB.

    Subclasses implement the domain-specific prompt engineering, logic, and
    structured output parsing for specialized agent roles while conforming to
    this unified contract.

    Attributes:
        _llm_factory: LLMProviderFactory instance for resolving LLM providers.
    """

    def __init__(
        self,
        llm_factory: LLMProviderFactory | None = None,
    ) -> None:
        """Initialize BaseAgent.

        Args:
            llm_factory: Optional LLMProviderFactory instance.
        """
        self._llm_factory = llm_factory or LLMProviderFactory()

    @property
    @abstractmethod
    def metadata(self) -> AgentMetadata:
        """Return metadata declaring the agent's identity and capabilities.

        Returns:
            An AgentMetadata instance describing this agent.
        """
        ...

    @abstractmethod
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the agent on a given request.

        Args:
            request: AgentRequest containing user prompt, context, and settings.

        Returns:
            An AgentResponse containing execution results and updated conversation.

        Raises:
            AgentValidationError: If input validation fails.
            AgentExecutionError: If execution fails during model interaction.
        """
        ...

    def validate_input(self, request: AgentRequest) -> bool:
        """Validate an incoming AgentRequest payload.

        Default implementation verifies that ``user_prompt`` is non-empty.
        Subclasses may override to add domain-specific schema validation.

        Args:
            request: The incoming AgentRequest payload.

        Returns:
            True if valid.

        Raises:
            AgentValidationError: If validation fails.
        """
        if not request.user_prompt or not request.user_prompt.strip():
            raise AgentValidationError(
                "User prompt cannot be empty",
                agent_id=self.metadata.id,
            )
        return True

    def validate_output(self, response: AgentResponse) -> bool:
        """Validate an outgoing AgentResponse payload.

        Default implementation verifies status is not FAILED. Subclasses may
        override to validate structured JSON or domain constraints.

        Args:
            response: The outgoing AgentResponse payload.

        Returns:
            True if valid.

        Raises:
            AgentValidationError: If output validation fails.
        """
        if response.status == AgentStatus.FAILED:
            raise AgentValidationError(
                f"Agent execution failed: {response.error}",
                agent_id=self.metadata.id,
            )
        return True

    async def health_check(self) -> bool:
        """Check whether the agent and its underlying LLM provider are healthy.

        Returns:
            True if healthy and operational, False otherwise.
        """
        try:
            # Check default provider health via factory
            provider_name = (
                self.metadata.supported_models[0]
                if self.metadata.supported_models
                else "openai"
            )
            if self._llm_factory.is_registered(provider_name):
                provider = self._llm_factory.get_provider(provider_name)
                return await provider.health_check()
            return True
        except Exception:
            return False
