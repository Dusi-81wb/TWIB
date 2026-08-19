"""SQLAlchemy 2.0 ORM models package.

This package exposes all persistence models for domain aggregates and execution records:

- :class:`.BaseModel`: Abstract base.
- :class:`.UserModel`: User ORM model.
- :class:`.OrganizationModel`: Organization ORM model.
- :class:`.OrganizationMemberModel`: Organization member ORM model.
- :class:`.WorkspaceModel`: Workspace ORM model.
- :class:`.WorkspaceMemberModel`: Workspace member ORM model.
- :class:`.ResearchExecutionModel`: ResearchAgent execution history model.
- :class:`.ResearchConversationModel`: ResearchAgent conversation model.
- :class:`.ResearchMessageModel`: ResearchAgent message turn model.
"""

from app.infrastructure.database.models.base_model import BaseModel
from app.infrastructure.database.models.organization_model import (
    OrganizationMemberModel,
    OrganizationModel,
)
from app.infrastructure.database.models.research_conversation_model import (
    ResearchConversationModel,
    ResearchMessageModel,
)
from app.infrastructure.database.models.research_execution_model import (
    ResearchExecutionModel,
)
from app.infrastructure.database.models.user_model import UserModel
from app.infrastructure.database.models.workspace_model import (
    WorkspaceMemberModel,
    WorkspaceModel,
)

__all__ = [
    "BaseModel",
    "OrganizationMemberModel",
    "OrganizationModel",
    "ResearchConversationModel",
    "ResearchExecutionModel",
    "ResearchMessageModel",
    "UserModel",
    "WorkspaceMemberModel",
    "WorkspaceModel",
]
