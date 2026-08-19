"""Tests for OptimizerAgent implementation."""

from collections.abc import AsyncIterator

import pytest

from app.agents import (
    AgentRequest,
    AgentStatus,
    AgentValidationError,
    OptimizerAgent,
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
    """Mock LLMProvider returning pre-set structured optimization JSON."""

    provider_name: str = "mock"

    def __init__(self, response_text: str = "") -> None:
        super().__init__()
        self._response_text = response_text

    async def complete(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            id="mock-opt-123",
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
            id="mock-opt-123",
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
async def test_optimizer_agent_successful_execution() -> None:
    valid_opt_json = """{
      "optimized_content": {
        "summary": "Optimized onboarding architecture"
      },
      "improvements_applied": [
        "Eliminated duplicate API definitions",
        "Condensed security description"
      ],
      "optimization_summary": "Improved conciseness by 25%",
      "confidence_score": 0.98
    }"""

    mock_provider = MockLLMProvider(response_text=valid_opt_json)
    factory = LLMProviderFactory()
    factory._instances["mock"] = mock_provider

    agent = OptimizerAgent(llm_factory=factory, default_provider="mock")
    assert agent.metadata.id == "optimizer"

    req = AgentRequest(
        agent_id="optimizer",
        user_prompt="Optimize architecture clarity",
        context={
            "validated_output": {
                "system_overview": "Original microservices overview",
            }
        },
        provider="mock",
    )
    res = await agent.execute(req)

    assert res.status == AgentStatus.COMPLETED
    assert res.result["confidence_score"] == 0.98
    assert len(res.result["improvements_applied"]) == 2


@pytest.mark.asyncio
async def test_optimizer_agent_missing_validated_output() -> None:
    agent = OptimizerAgent()
    req = AgentRequest(
        agent_id="optimizer",
        user_prompt="Optimize content",
        context={},
    )
    with pytest.raises(AgentValidationError):
        await agent.execute(req)
