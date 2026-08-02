"""Repository interfaces.

This package defines the persistence contracts of the platform. It contains
the generic :class:`~app.domain.repositories.base.Repository` contract, the
business-oriented aggregate repositories (:class:`UserRepository`,
:class:`OrganizationRepository`, :class:`WorkspaceRepository`), and the
:class:`~app.domain.repositories.unit_of_work.UnitOfWork` that groups them
into a single business transaction.

Everything here is a pure-Python interface (``typing.Protocol``). There is no
SQLAlchemy, database, ORM, or infrastructure code: concrete implementations
belong to the database infrastructure phase.
"""

from __future__ import annotations

from app.domain.repositories.base import Repository
from app.domain.repositories.organization_repository import OrganizationRepository
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.workspace_repository import WorkspaceRepository

__all__ = [
    "OrganizationRepository",
    "Repository",
    "UnitOfWork",
    "UserRepository",
    "WorkspaceRepository",
]
