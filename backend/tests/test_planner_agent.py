"""Tests for PlannerAgent implementation."""

from collections.abc import AsyncIterator

import pytest

from app.agents import (
    AgentRequest,
    AgentStatus,
    AgentValidationError,
    PlannerAgent,
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
    """Mock LLMProvider returning pre-set structured JSON."""

    provider_name: str = "mock"

    def __init__(self, response_text: str = "") -> None:
        super().__init__()
        self._response_text = response_text

    async def complete(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            id="mock-123",
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
            id="mock-123",
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
async def test_planner_agent_successful_execution() -> None:
    valid_plan_json = """{
      "goal": "Build an automated onboarding pipeline",
      "assumptions": ["User has valid account"],
      "objectives": ["Provision user", "Send welcome email"],
      "required_tasks": [
        {
          "id": "t1",
          "name": "Provisioning",
          "description": "Create account",
          "dependencies": []
        },
        {
          "id": "t2",
          "name": "Notification",
          "description": "Send welcome email",
          "dependencies": ["t1"]
        }
      ],
      "task_dependencies": [{"task_id": "t2", "depends_on": ["t1"]}],
      "risks": ["Email server timeout"],
      "expected_output": "Fully provisioned user account"
    }"""

    mock_provider = MockLLMProvider(response_text=valid_plan_json)
    factory = LLMProviderFactory()
    factory.register_provider("mock", type(mock_provider))
    # Register mock instance
    factory._instances["mock"] = mock_provider

    agent = PlannerAgent(llm_factory=factory, default_provider="mock")
    assert agent.metadata.id == "planner"

    req = AgentRequest(
        agent_id="planner",
        user_prompt="Build an automated onboarding pipeline",
        provider="mock",
    )
    res = await agent.execute(req)

    assert res.status == AgentStatus.COMPLETED
    assert res.result["goal"] == "Build an automated onboarding pipeline"
    assert len(res.result["required_tasks"]) == 2


@pytest.mark.asyncio
async def test_planner_agent_invalid_input() -> None:
    agent = PlannerAgent()
    req = AgentRequest(agent_id="planner", user_prompt="  ")
    with pytest.raises(AgentValidationError):
        await agent.execute(req)


@pytest.mark.asyncio
async def test_planner_agent_malformed_llm_json() -> None:
    mock_provider = MockLLMProvider(response_text="Not valid json")
    factory = LLMProviderFactory()
    factory._instances["mock"] = mock_provider

    agent = PlannerAgent(llm_factory=factory, default_provider="mock")
    req = AgentRequest(
        agent_id="planner",
        user_prompt="Create a custom reporting system",
        provider="mock",
    )
    with pytest.raises(AgentValidationError):
        await agent.execute(req)
