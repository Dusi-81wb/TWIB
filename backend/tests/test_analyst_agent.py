"""Tests for AnalystAgent implementation."""

from collections.abc import AsyncIterator

import pytest

from app.agents import (
    AgentRequest,
    AgentStatus,
    AgentValidationError,
    AnalystAgent,
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


class MockLLMProvider(LLMProvider):
    """Mock LLMProvider returning pre-set structured analysis JSON."""

    provider_name: str = "mock"

    def __init__(self, response_text: str = "") -> None:
        super().__init__()
        self._response_text = response_text

    async def complete(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            id="mock-ana-123",
            model=request.model,
            provider=self.provider_name,
            message=ChatMessage(
                role=MessageRole.ASSISTANT,
                content=self._response_text,
            ),
            finish_reason="stop",
            usage=CompletionUsage(
                prompt_tokens=10, completion_tokens=20, total_tokens=30
            ),
        )

    async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        yield StreamChunk(
            id="mock-ana-123",
            model=request.model,
            provider=self.provider_name,
            delta=self._response_text,
            finish_reason="stop",
        )

    async def list_models(self) -> list[ModelInfo]:
        return []

    async def health_check(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_analyst_agent_successful_execution() -> None:
    valid_analysis_json = """{
      "business_requirements": ["Automate onboarding workflow"],
      "functional_requirements": ["Send SMS notification on signup"],
      "non_functional_requirements": ["Sub-second API response time"],
      "constraints": ["Must use PostgreSQL"],
      "assumptions": ["Users have valid phone numbers"],
      "risks": ["Third party SMS gateway downtime"],
      "success_criteria": ["99.9% notification delivery rate"]
    }"""

    mock_provider = MockLLMProvider(response_text=valid_analysis_json)
    factory = LLMProviderFactory()
    factory._instances["mock"] = mock_provider

    agent = AnalystAgent(llm_factory=factory, default_provider="mock")
    assert agent.metadata.id == "analyst"

    req = AgentRequest(
        agent_id="analyst",
        user_prompt="Analyze requirements for user onboarding",
        context={
            "planning_result": {"goal": "Build onboarding"},
            "research_result": {"summary": "SMS is preferred"},
        },
        provider="mock",
    )
    res = await agent.execute(req)

    assert res.status == AgentStatus.COMPLETED
    assert len(res.result["functional_requirements"]) == 1
    assert len(res.result["business_requirements"]) == 1


@pytest.mark.asyncio
async def test_analyst_agent_missing_planning_result() -> None:
    agent = AnalystAgent()
    req = AgentRequest(
        agent_id="analyst",
        user_prompt="Analyze requirements",
        context={"research_result": {"summary": "Some research"}},
    )
    with pytest.raises(AgentValidationError):
        await agent.execute(req)


@pytest.mark.asyncio
async def test_analyst_agent_missing_research_result() -> None:
    agent = AnalystAgent()
    req = AgentRequest(
        agent_id="analyst",
        user_prompt="Analyze requirements",
        context={"planning_result": {"goal": "Some goal"}},
    )
    with pytest.raises(AgentValidationError):
        await agent.execute(req)
