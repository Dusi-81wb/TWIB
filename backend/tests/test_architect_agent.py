"""Tests for ArchitectAgent implementation."""

from collections.abc import AsyncIterator

import pytest

from app.agents import (
    AgentRequest,
    AgentStatus,
    AgentValidationError,
    ArchitectAgent,
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
    """Mock LLMProvider returning pre-set structured architecture JSON."""

    provider_name: str = "mock"

    def __init__(self, response_text: str = "") -> None:
        super().__init__()
        self._response_text = response_text

    async def complete(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            id="mock-arch-123",
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
            id="mock-arch-123",
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
async def test_architect_agent_successful_execution() -> None:
    valid_design_json = """{
      "system_overview": "Microservice-based onboarding architecture",
      "components": ["API Gateway", "Auth Service", "Worker Engine"],
      "services": ["User Provisioning Service", "Notification Service"],
      "data_flow": ["API Gateway -> Auth Service -> Database"],
      "api_requirements": ["POST /api/v1/onboard"],
      "database_design": "Relational PostgreSQL schema with ACID compliance",
      "external_integrations": ["Twilio SMS API"],
      "scalability_considerations": ["Horizontal pod autoscaling"],
      "security_considerations": ["OAuth2 JWT Bearer tokens"],
      "deployment_considerations": ["Containerized Docker on Kubernetes"]
    }"""

    mock_provider = MockLLMProvider(response_text=valid_design_json)
    factory = LLMProviderFactory()
    factory._instances["mock"] = mock_provider

    agent = ArchitectAgent(llm_factory=factory, default_provider="mock")
    assert agent.metadata.id == "architect"

    req = AgentRequest(
        agent_id="architect",
        user_prompt="Design system architecture for onboarding",
        context={
            "analysis_result": {
                "business_requirements": ["Automate onboarding"],
                "functional_requirements": ["Send SMS"],
            }
        },
        provider="mock",
    )
    res = await agent.execute(req)

    assert res.status == AgentStatus.COMPLETED
    assert res.result["system_overview"] == "Microservice-based onboarding architecture"
    assert len(res.result["components"]) == 3


@pytest.mark.asyncio
async def test_architect_agent_missing_analysis_result() -> None:
    agent = ArchitectAgent()
    req = AgentRequest(
        agent_id="architect",
        user_prompt="Design architecture",
        context={},
    )
    with pytest.raises(AgentValidationError):
        await agent.execute(req)
