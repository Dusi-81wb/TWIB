"""Unit of Work interface.

A unit of work groups all repository operations for a single business
transaction and exposes one commit point, so a use case either persists
completely or not at all. This module declares the
:class:`~app.domain.repositories.unit_of_work.UnitOfWork` contract; a concrete
implementation (session-bound repositories, ``commit()``, ``rollback()``) is
provided by the database infrastructure phase.
"""

from __future__ import annotations

from typing import Any, Protocol

from app.domain.repositories.organization_repository import OrganizationRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.workspace_repository import WorkspaceRepository


class UnitOfWork(Protocol):
    """Transaction boundary that coordinates the aggregate repositories.

    A unit of work owns the three aggregate repositories and exposes a single
    :meth:`commit` point, so a business operation either persists completely
    or not at all. The repositories are exposed as plain attributes; an
    implementation returns request-scoped (or session-bound) repository
    instances. A use case acquires one unit of work, performs its repository
    operations, and calls :meth:`commit` exactly once (or :meth:`rollback` on
    failure).
    """

    users: UserRepository
    organizations: OrganizationRepository
    workspaces: WorkspaceRepository

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
