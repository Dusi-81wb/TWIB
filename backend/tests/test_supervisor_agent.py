"""Tests for SupervisorAgent implementation."""

from collections.abc import AsyncIterator
from typing import Any

import pytest

from app.agents import (
    AgentRequest,
    AgentStatus,
    AgentValidationError,
    BaseAgent,
    SupervisorAgent,
)
from app.infrastructure.llm.factory import LLMProviderFactory
from app.infrastructure.llm.message import ChatMessage, MessageRole
from app.infrastructure.llm.models import ModelInfo
from app.infrastructure.llm.provider import LLMProvider
from app.infrastructure.llm.response import (
    ChatRequest,
    ChatResponse,
    CompletionUsage,
    StreamChunk,
)


class DummyChildAgent(BaseAgent):
    """Dummy agent for testing supervisor step execution."""

    def __init__(self, agent_id: str, return_data: str) -> None:
        super().__init__()
        self._agent_id = agent_id
        self._return_data = return_data

    async def execute(self, request: AgentRequest) -> Any:
        from app.agents.models import AgentResponse, AgentStatus

        return AgentResponse(
            agent_id=self._agent_id,
            status=AgentStatus.COMPLETED,
            result={
                "step_output": self._return_data,
                "context_received": request.context,
            },
        )

    @property
    def metadata(self) -> Any:
        from app.agents.models import AgentMetadata

        return AgentMetadata(
            id=self._agent_id,
            name=f"Dummy {self._agent_id}",
            description="Dummy agent",
            version="1.0.0",
        )


class MockLLMProvider(LLMProvider):
    """Mock LLMProvider."""

    provider_name: str = "mock"

    async def complete(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            id="mock-sup-123",
            model=request.model,
            provider=self.provider_name,
            message=ChatMessage(
                role=MessageRole.ASSISTANT,
                content="{}",
            ),
            finish_reason="stop",
            usage=CompletionUsage(
                prompt_tokens=10, completion_tokens=20, total_tokens=30
            ),
        )

    async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        yield StreamChunk(
            id="mock-sup-123",
            model=request.model,
            provider=self.provider_name,
            delta="{}",
            finish_reason="stop",
        )

    async def list_models(self) -> list[ModelInfo]:
        return []

    async def health_check(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_supervisor_agent_pipeline_execution() -> None:
    factory = LLMProviderFactory()
    factory._instances["mock"] = MockLLMProvider()

    dummy_registry: dict[str, BaseAgent] = {
        "planner": DummyChildAgent("planner", "plan_data"),
        "research": DummyChildAgent("research", "research_data"),
    }

    supervisor = SupervisorAgent(
        llm_factory=factory,
        default_provider="mock",
        agent_registry=dummy_registry,
    )
    assert supervisor.metadata.id == "supervisor"

    req = AgentRequest(
        agent_id="supervisor",
        user_prompt="Build onboarding platform",
        context={"agent_pipeline": ["planner", "research"]},
        provider="mock",
    )
    res = await supervisor.execute(req)

    assert res.status == AgentStatus.COMPLETED
    assert len(res.result["executed_steps"]) == 2
    assert res.result["executed_steps"][0]["agent_id"] == "planner"
    assert res.result["executed_steps"][1]["agent_id"] == "research"


@pytest.mark.asyncio
async def test_supervisor_agent_empty_prompt() -> None:
    supervisor = SupervisorAgent()
    req = AgentRequest(
        agent_id="supervisor",
        user_prompt="",
    )
    with pytest.raises(AgentValidationError):
        await supervisor.execute(req)
