"""SQLAlchemy Unit of Work implementation.

Coordinates User, Organization, Workspace, and Workflow aggregate repositories
over a single AsyncSession transaction boundary.
"""

from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.unit_of_work import UnitOfWork
from app.infrastructure.repositories.organization_repository import (
    SQLAlchemyOrganizationRepository,
)
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.repositories.workflow_repository import (
    WorkflowCheckpointRepository,
    WorkflowExecutionRepository,
    WorkflowRepository,
)
from app.infrastructure.repositories.workspace_repository import (
    SQLAlchemyWorkspaceRepository,
)


class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of the UnitOfWork contract."""

    users: SQLAlchemyUserRepository
    organizations: SQLAlchemyOrganizationRepository
    workspaces: SQLAlchemyWorkspaceRepository
    workflows: WorkflowRepository
    workflow_executions: WorkflowExecutionRepository
    workflow_checkpoints: WorkflowCheckpointRepository

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the Unit of Work bound to an AsyncSession."""
        self._session = session
        self.users = SQLAlchemyUserRepository(session)
        self.organizations = SQLAlchemyOrganizationRepository(session)
        self.workspaces = SQLAlchemyWorkspaceRepository(session)
        self.workflows = WorkflowRepository(session)
        self.workflow_executions = WorkflowExecutionRepository(session)
        self.workflow_checkpoints = WorkflowCheckpointRepository(session)

    async def commit(self) -> None:
        """Commit the active database transaction."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Roll back the active database transaction."""
        await self._session.rollback()

    async def close(self) -> None:
        """Close the AsyncSession."""
        await self._session.close()

    async def __aenter__(self) -> Self:
        """Enter the async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context manager, rolling back on exception."""
        if exc_type is not None:
            await self.rollback()
        await self.close()
