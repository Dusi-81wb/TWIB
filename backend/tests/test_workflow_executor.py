"""Tests for WorkflowExecutor implementation."""

from collections.abc import AsyncIterator
from typing import Any

import pytest

from app.agents.base_agent import BaseAgent
from app.agents.models import AgentRequest, AgentResponse, AgentStatus
from app.agents.supervisor_agent import SupervisorAgent
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
from app.workflows import (
    WorkflowEngine,
    WorkflowExecutor,
    WorkflowStateError,
    WorkflowStatus,
)


class DummyAgent(BaseAgent):
    """Dummy agent for mocking supervisor pipeline steps."""

    def __init__(self, agent_id: str) -> None:
        super().__init__()
        self._agent_id = agent_id

    async def execute(self, request: AgentRequest) -> AgentResponse:
        return AgentResponse(
            agent_id=self._agent_id,
            status=AgentStatus.COMPLETED,
            result={"step": self._agent_id, "data": "output_ok"},
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
            id="mock-exec-123",
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
            id="mock-exec-123",
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
async def test_workflow_executor_full_execution() -> None:
    events_emitted: list[str] = []

    def event_listener(event_type: str, payload: dict) -> None:
        events_emitted.append(event_type)

    factory = LLMProviderFactory()
    factory._instances["mock"] = MockLLMProvider()

    dummy_registry: dict[str, BaseAgent] = {
        "planner": DummyAgent("planner"),
        "research": DummyAgent("research"),
    }

    supervisor = SupervisorAgent(
        llm_factory=factory,
        default_provider="mock",
        agent_registry=dummy_registry,
    )

    engine = WorkflowEngine(supervisor_agent=supervisor)
    executor = WorkflowExecutor(
        engine=engine,
        supervisor_agent=supervisor,
        event_listener=event_listener,
    )

    wf = engine.create_workflow(
        workflow_name="Full Workflow Test",
        user_request="Build product architecture",
        metadata={"context": {"agent_pipeline": ["planner", "research"]}},
    )

    executed_wf = await executor.execute(wf)

    assert executed_wf.workflow_status == WorkflowStatus.COMPLETED
    assert len(executed_wf.execution_steps) == 2
    assert "workflow.started" in events_emitted
    assert "workflow.completed" in events_emitted


@pytest.mark.asyncio
async def test_workflow_executor_pause_stop_resume() -> None:
    engine = WorkflowEngine()
    executor = WorkflowExecutor(engine=engine)

    wf = engine.create_workflow("Control Test", "Test controls")
    wf.mark_running()

    paused_wf = executor.pause_execution(wf)
    assert paused_wf.workflow_status == WorkflowStatus.PAUSED

    stopped_wf = executor.stop_execution(wf)
    assert stopped_wf.workflow_status == WorkflowStatus.CANCELLED

    with pytest.raises(WorkflowStateError):
        await executor.resume_execution(stopped_wf)
