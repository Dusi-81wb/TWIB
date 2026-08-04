"""Workflow Realtime Events domain models and event publisher.

Defines structured event types, event payload models, and central event publisher
for workflow lifecycle and agent execution progress updates.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class WorkflowEventType(StrEnum):
    """Supported realtime event types for workflows and agents."""

    WORKFLOW_CREATED = "workflow.created"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_PROGRESS = "workflow.progress"
    WORKFLOW_PAUSED = "workflow.paused"
    WORKFLOW_WAITING_FOR_APPROVAL = "workflow.waiting_for_approval"
    WORKFLOW_RESUMED = "workflow.resumed"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_CANCELLED = "workflow.cancelled"
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"


class WorkflowEvent(BaseModel):
    """Structured event payload for realtime workflow updates."""

    workflow_id: str = Field(..., description="Target workflow identity UUID string.")
    event_type: str = Field(..., description="Type of event emitted.")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 timestamp string.",
    )
    current_state: str | None = Field(
        default=None, description="Current workflow state status."
    )
    current_agent: str | None = Field(
        default=None, description="Active executing agent ID if applicable."
    )
    progress: float | None = Field(
        default=None, ge=0.0, le=100.0, description="Execution progress percentage."
    )
    message: str | None = Field(
        default=None, description="Human-readable message or error description."
    )
    data: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary event data payload."
    )


class WorkflowEventPublisher:
    """Central event publisher for dispatching workflow events."""

    def __init__(self) -> None:
        """Initialize WorkflowEventPublisher."""
        self._listeners: list[Callable[[WorkflowEvent], Any]] = []
        self._background_tasks: set[Any] = set()

    def register_listener(self, listener: Callable[[WorkflowEvent], Any]) -> None:
        """Register an event listener callback."""
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unregister_listener(self, listener: Callable[[WorkflowEvent], Any]) -> None:
        """Unregister an event listener callback."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def publish(self, event: WorkflowEvent) -> None:
        """Dispatch a WorkflowEvent to all registered listeners."""
        import contextlib

        for listener in list(self._listeners):
            with contextlib.suppress(Exception):
                res = listener(event)
                if hasattr(res, "__await__"):
                    import asyncio

                    with contextlib.suppress(Exception):
                        loop = asyncio.get_running_loop()
                        task = loop.create_task(res)
                        self._background_tasks.add(task)
                        task.add_done_callback(self._background_tasks.discard)
