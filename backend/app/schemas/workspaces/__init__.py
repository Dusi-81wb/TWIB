"""Workspace schemas package.

Exposes request and response schemas for workspace management:

- :class:`.WorkspaceResponse`: Individual workspace response.
- :class:`.WorkspaceListResponse`: Paginated list response.
- :class:`.CreateWorkspaceRequest`: Workspace creation request.
- :class:`.UpdateWorkspaceRequest`: Workspace update request.
"""

from app.schemas.workspaces.create_workspace_request import (
    CreateWorkspaceRequest,
)
from app.schemas.workspaces.update_workspace_request import (
    UpdateWorkspaceRequest,
)
from app.schemas.workspaces.workspace_response import (
    WorkspaceListResponse,
    WorkspaceMemberResponse,
    WorkspaceResponse,
)

__all__ = [
    "CreateWorkspaceRequest",
    "UpdateWorkspaceRequest",
    "WorkspaceListResponse",
    "WorkspaceMemberResponse",
    "WorkspaceResponse",
]
