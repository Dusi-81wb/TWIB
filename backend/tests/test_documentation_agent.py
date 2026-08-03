"""Tests for DocumentationAgent implementation."""

from collections.abc import AsyncIterator

import pytest

from app.agents import (
    AgentRequest,
    AgentStatus,
    AgentValidationError,
    DocType,
    DocumentationAgent,
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
    """Mock LLMProvider returning pre-set structured documentation JSON."""

    provider_name: str = "mock"

    def __init__(self, response_text: str = "") -> None:
        super().__init__()
        self._response_text = response_text

    async def complete(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            id="mock-doc-123",
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
            id="mock-doc-123",
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
async def test_documentation_agent_successful_execution() -> None:
    valid_doc_json = """{
      "doc_type": "readme",
      "title": "Onboarding Service Readme",
      "summary": "Overview of onboarding pipeline.",
      "sections": [
        {"heading": "Overview", "content": "Onboarding pipeline docs."},
        {"heading": "Installation", "content": "Run `uv sync`."}
      ],
      "markdown_content": "# Onboarding Service Readme\\n\\nDocs summary."
    }"""

    mock_provider = MockLLMProvider(response_text=valid_doc_json)
    factory = LLMProviderFactory()
    factory._instances["mock"] = mock_provider

    agent = DocumentationAgent(llm_factory=factory, default_provider="mock")
    assert agent.metadata.id == "documentation"

    req = AgentRequest(
        agent_id="documentation",
        user_prompt="Generate README documentation",
        context={
            "optimized_output": {"summary": "Microservices design"},
            "documentation_type": DocType.README,
        },
        provider="mock",
    )
    res = await agent.execute(req)

    assert res.status == AgentStatus.COMPLETED
    assert res.result["doc_type"] == "readme"
    assert len(res.result["sections"]) == 2


@pytest.mark.asyncio
async def test_documentation_agent_missing_optimized_output() -> None:
    agent = DocumentationAgent()
    req = AgentRequest(
        agent_id="documentation",
        user_prompt="Generate README",
        context={"documentation_type": DocType.README},
    )
    with pytest.raises(AgentValidationError):
        await agent.execute(req)


@pytest.mark.asyncio
async def test_documentation_agent_unsupported_doc_type() -> None:
    agent = DocumentationAgent()
    req = AgentRequest(
        agent_id="documentation",
        user_prompt="Generate doc",
        context={
            "optimized_output": {"summary": "test"},
            "documentation_type": "completely_invalid_type_xyz",
        },
    )
    with pytest.raises(AgentValidationError):
        await agent.execute(req)
