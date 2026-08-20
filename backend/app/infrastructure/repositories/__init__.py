"""SQLAlchemy repository implementations package.

Exposes concrete repositories and Unit of Work backing domain contracts:

- :class:`.BaseRepository`: Generic repository base.
- :class:`.SQLAlchemyUserRepository`: User repository.
- :class:`.SQLAlchemyOrganizationRepository`: Organization repository.
- :class:`.SQLAlchemyWorkspaceRepository`: Workspace repository.
- :class:`.WorkflowRepository`: Workflow repository.
- :class:`.WorkflowExecutionRepository`: Workflow execution repository.
- :class:`.WorkflowCheckpointRepository`: Workflow checkpoint repository.
- :class:`.SQLAlchemyResearchExecutionRepository`: Research execution repository.
- :class:`.SQLAlchemyUnitOfWork`: Unit of Work.
"""

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.repositories.organization_repository import (
    SQLAlchemyOrganizationRepository,
)
from app.infrastructure.repositories.research_execution_repository import (
    SQLAlchemyResearchExecutionRepository,
)
from app.infrastructure.repositories.unit_of_work import SQLAlchemyUnitOfWork
from app.infrastructure.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from app.infrastructure.repositories.workflow_repository import (
    WorkflowCheckpointRepository,
    WorkflowExecutionRepository,
    WorkflowRepository,
)
from app.infrastructure.repositories.workspace_repository import (
    SQLAlchemyWorkspaceRepository,
)

__all__ = [
    "BaseRepository",
    "SQLAlchemyOrganizationRepository",
    "SQLAlchemyResearchExecutionRepository",
    "SQLAlchemyUnitOfWork",
    "SQLAlchemyUserRepository",
    "SQLAlchemyWorkspaceRepository",
    "WorkflowCheckpointRepository",
    "WorkflowExecutionRepository",
    "WorkflowRepository",
]
