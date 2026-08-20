"""Workflow domain repository interfaces.

Defines persistence contracts for Workflow, WorkflowExecution, and WorkflowCheckpoint aggregates.
"""

from __future__ import annotations

from typing import Protocol

from app.domain.repositories.base import Repository
from app.domain.workflows.entities import (
    Workflow,
    WorkflowCheckpoint,
    WorkflowExecution,
)


class IWorkflowRepository(Repository[Workflow, str], Protocol):
    """Domain repository interface for Workflow aggregates."""

    async def get_by_id(self, id_: str) -> Workflow | None:
        """Load a Workflow aggregate by its unique identity string."""
        ...

    async def list_by_workspace(
        self,
        workspace_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Workflow]:
        """List workflows matching an optional workspace ID with pagination."""
        ...

    async def count_by_workspace(self, workspace_id: str | None = None) -> int:
        """Return total count of workflows."""
        ...


class IWorkflowExecutionRepository(Repository[WorkflowExecution, str], Protocol):
    """Domain repository interface for WorkflowExecution aggregates."""

    async def get_by_id(self, id_: str) -> WorkflowExecution | None:
        """Load a WorkflowExecution by its unique execution ID."""
        ...

    async def list_by_workflow(
        self,
        workflow_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[WorkflowExecution]:
        """List executions for a given workflow ordered by start time descending."""
        ...

    async def get_latest_by_workflow(self, workflow_id: str) -> WorkflowExecution | None:
        """Get the most recent execution for a workflow."""
        ...


class IWorkflowCheckpointRepository(Repository[WorkflowCheckpoint, str], Protocol):
    """Domain repository interface for WorkflowCheckpoint entities."""

    async def get_by_id(self, id_: str) -> WorkflowCheckpoint | None:
        """Load a checkpoint by ID."""
        ...

    async def list_by_execution(self, execution_id: str) -> list[WorkflowCheckpoint]:
        """List all checkpoints associated with an execution."""
        ...

    async def list_pending_by_workflow(self, workflow_id: str) -> list[WorkflowCheckpoint]:
        """List pending review checkpoints for a workflow."""
        ...
