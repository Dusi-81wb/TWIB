"""Generic repository interface.

A repository abstracts persistence behind a domain-owned interface so the
domain and application layers never depend on a database, ORM, or framework.
This module defines the generic :class:`Repository` persistence contract.

Concrete aggregate repositories are intentionally small and business-oriented
(see :mod:`app.domain.repositories.user_repository`,
:mod:`app.domain.repositories.organization_repository`, and
:mod:`app.domain.repositories.workspace_repository`): they expose the queries
the application actually needs instead of an unrestricted generic CRUD
surface. This module depends only on the standard library and the domain
layer, so it stays framework-independent.
"""

from __future__ import annotations

import uuid
from typing import Any, Protocol

from app.domain.entity import Entity


class Repository[TEntity: Entity[Any], TID: uuid.UUID | str | int](Protocol):
    """Generic persistence contract for an aggregate.

    Every aggregate repository implements the common operations of loading an
    aggregate by identity, checking existence, saving a whole aggregate, and
    deleting it. Repositories always persist aggregates as a whole (per the
    Aggregate Root pattern) and never contain business rules.

    This is a protocol, so it is satisfied structurally: any object providing
    these methods is a valid repository. A concrete infrastructure
    implementation (for example a SQLAlchemy-backed repository) will fulfill
    this contract in a later phase.

    Type parameters:
        TEntity: The aggregate root type persisted by the repository.
        TID: The identity type used to address aggregates.
    """

    async def get_by_id(self, id_: TID) -> TEntity | None:
        """Load an aggregate by its identity.

        Args:
            id_: The identity of the aggregate to load.

        Returns:
            The aggregate, or ``None`` when no aggregate has that identity.
        """
        ...

    async def exists(self, id_: TID) -> bool:
        """Return whether an aggregate with the identity exists.

        Args:
            id_: The identity to check.

        Returns:
            True when an aggregate with that identity is persisted.
        """
        ...

    async def save(self, entity: TEntity) -> None:
        """Persist an aggregate, inserting or updating it as needed.

        Args:
            entity: The aggregate root to persist.
        """
        ...

    async def delete(self, id_: TID) -> None:
        """Delete the aggregate with the identity.

        Args:
            id_: The identity of the aggregate to delete.
        """
        ...
