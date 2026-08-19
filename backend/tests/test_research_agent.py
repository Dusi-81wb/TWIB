"""Tests for ResearchAgent implementation."""

from collections.abc import AsyncIterator

import pytest

from app.agents import (
    AgentRequest,
    AgentStatus,
    AgentValidationError,
    ResearchAgent,
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
    """Mock LLMProvider returning pre-set structured research JSON."""

    provider_name: str = "mock"

    def __init__(self, response_text: str = "") -> None:
        super().__init__()
        self._response_text = response_text

    async def complete(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            id="mock-res-123",
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
            id="mock-res-123",
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
async def test_research_agent_successful_execution() -> None:
    valid_report_json = """{
      "topic": "OAuth2 PKCE flow for mobile apps",
      "summary": "PKCE prevents authorization code interception attacks.",
      "key_findings": ["Use S256 code challenge method"],
      "best_practices": ["Short authorization code TTL"],
      "risks": ["PlainText challenge method downgrade"],
      "references": ["RFC 7636"],
      "recommendations": ["Enforce PKCE globally"]
    }"""

    mock_provider = MockLLMProvider(response_text=valid_report_json)
    factory = LLMProviderFactory()
    factory._instances["mock"] = mock_provider

    agent = ResearchAgent(llm_factory=factory, default_provider="mock")
    assert agent.metadata.id == "researcher"

    req = AgentRequest(
        agent_id="researcher",
        user_prompt="OAuth2 PKCE flow for mobile apps",
        provider="mock",
    )
    res = await agent.execute(req)

    assert res.status == AgentStatus.COMPLETED
    assert res.result["topic"] == "OAuth2 PKCE flow for mobile apps"
    assert len(res.result["key_findings"]) == 1


@pytest.mark.asyncio
async def test_research_agent_invalid_input() -> None:
    agent = ResearchAgent()
    req = AgentRequest(agent_id="researcher", user_prompt=" ")
    with pytest.raises(AgentValidationError):
        await agent.execute(req)


@pytest.mark.asyncio
async def test_research_agent_malformed_json() -> None:
    mock_provider = MockLLMProvider(response_text="Plain unparseable output")
    factory = LLMProviderFactory()
    factory._instances["mock"] = mock_provider

    agent = ResearchAgent(llm_factory=factory, default_provider="mock")
    req = AgentRequest(
        agent_id="researcher",
        user_prompt="Microservices communication patterns",
        provider="mock",
    )
    with pytest.raises(AgentValidationError):
        await agent.execute(req)
