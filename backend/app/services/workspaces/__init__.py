"""Workspace services package.

Provides the application service for workspace management:

- :class:`.WorkspaceService`: Workspace CRUD operations.
"""

from app.services.workspaces.workspace_service import WorkspaceService

__all__ = ["WorkspaceService"]
