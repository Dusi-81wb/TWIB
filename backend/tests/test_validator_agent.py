"""Tests for ValidatorAgent implementation."""

from collections.abc import AsyncIterator

import pytest

from app.agents import (
    AgentRequest,
    AgentStatus,
    AgentValidationError,
    ValidationStatus,
    ValidatorAgent,
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
    """Mock LLMProvider returning pre-set structured validation JSON."""

    provider_name: str = "mock"

    def __init__(self, response_text: str = "") -> None:
        super().__init__()
        self._response_text = response_text

    async def complete(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            id="mock-val-123",
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
            id="mock-val-123",
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
async def test_validator_agent_successful_execution() -> None:
    valid_report_json = """{
      "status": "pass",
      "confidence_score": 0.95,
      "issues_found": [],
      "missing_information": [],
      "contradictions": [],
      "suggested_improvements": ["Add automated load testing"]
    }"""

    mock_provider = MockLLMProvider(response_text=valid_report_json)
    factory = LLMProviderFactory()
    factory._instances["mock"] = mock_provider

    agent = ValidatorAgent(llm_factory=factory, default_provider="mock")
    assert agent.metadata.id == "validator"

    req = AgentRequest(
        agent_id="validator",
        user_prompt="Validate architecture output",
        context={
            "agent_output": {
                "system_overview": "Microservices design",
                "components": ["API Gateway"],
            }
        },
        provider="mock",
    )
    res = await agent.execute(req)

    assert res.status == AgentStatus.COMPLETED
    assert res.result["status"] == ValidationStatus.PASS
    assert res.result["confidence_score"] == 0.95


@pytest.mark.asyncio
async def test_validator_agent_missing_agent_output() -> None:
    agent = ValidatorAgent()
    req = AgentRequest(
        agent_id="validator",
        user_prompt="Validate output",
        context={},
    )
    with pytest.raises(AgentValidationError):
        await agent.execute(req)
