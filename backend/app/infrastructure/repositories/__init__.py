"""SQLAlchemy repository implementations package.

This package exposes the concrete repositories and Unit of Work backing the
domain layer contracts:

- :class:`.BaseRepository`: Generic repository base.
- :class:`.SQLAlchemyUserRepository`: User repository.
- :class:`.SQLAlchemyOrganizationRepository`: Organization repository.
- :class:`.SQLAlchemyWorkspaceRepository`: Workspace repository.
- :class:`.SQLAlchemyUnitOfWork`: Unit of Work.
"""

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.repositories.organization_repository import (
    SQLAlchemyOrganizationRepository,
)
from app.infrastructure.repositories.unit_of_work import SQLAlchemyUnitOfWork
from app.infrastructure.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from app.infrastructure.repositories.workspace_repository import (
    SQLAlchemyWorkspaceRepository,
)

__all__ = [
    "BaseRepository",
    "SQLAlchemyOrganizationRepository",
    "SQLAlchemyUnitOfWork",
    "SQLAlchemyUserRepository",
    "SQLAlchemyWorkspaceRepository",
]
