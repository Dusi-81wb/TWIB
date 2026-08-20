"""Unit of Work interface.

A unit of work groups all repository operations for a single business
transaction and exposes one commit point, so a use case either persists
completely or not at all.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from app.domain.repositories.organization_repository import OrganizationRepository
    from app.domain.repositories.user_repository import UserRepository
    from app.domain.repositories.workspace_repository import WorkspaceRepository
    from app.domain.workflows.repositories import (
        IWorkflowCheckpointRepository,
        IWorkflowExecutionRepository,
        IWorkflowRepository,
    )


class UnitOfWork(Protocol):
    """Transaction boundary that coordinates the aggregate repositories."""

    users: Any
    organizations: Any
    workspaces: Any
    workflows: Any
    workflow_executions: Any
    workflow_checkpoints: Any

    async def commit(self) -> None:
        """Commit the current transaction, persisting every change."""
        ...

    async def rollback(self) -> None:
        """Roll back the current transaction, discarding every change."""
        ...

    async def close(self) -> None:
        """Close the underlying session resources."""
        ...

    async def __aenter__(self) -> UnitOfWork:
        """Enter the async context manager."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit the async context manager."""
        ...
