"""Workspace domain package.

This package models the workspace aggregate, the collaboration boundary inside
an organization. It contains the
:class:`~app.domain.workspaces.workspace.Workspace` aggregate root, the
immutable :class:`~app.domain.workspaces.membership.WorkspaceMembership` domain
object with its :class:`~app.domain.workspaces.membership.WorkspaceRole` and
:class:`~app.domain.workspaces.membership.WorkspaceMembershipStatus` enums, the
immutable :class:`~app.domain.workspaces.settings.WorkspaceSettings` domain
object with its :class:`~app.domain.workspaces.settings.WorkspaceVisibility`
enum, the :class:`~app.domain.workspaces.status.WorkspaceStatus` domain enum,
the workspace domain events, and the workspace business-rule exceptions.

Everything here is pure Python (standard library only) and depends on the
Phase 2.1 domain foundation, the Phase 2.2 value objects, and the Phase 2.3/2.4
user and organization domains. It contains no authentication, database,
billing, repository, or API code.
"""

from __future__ import annotations

from app.domain.workspaces.events import (
    WorkspaceCreated,
    WorkspaceMemberAdded,
    WorkspaceMemberRemoved,
    WorkspaceOwnerChanged,
    WorkspaceRenamed,
    WorkspaceSettingsChanged,
)
from app.domain.workspaces.exceptions import (
    DuplicateWorkspaceMember,
    InvalidWorkspaceState,
    OwnerCannotBeRemoved,
    WorkspaceAlreadyExists,
    WorkspaceArchived,
)
from app.domain.workspaces.membership import (
    WorkspaceMembership,
    WorkspaceMembershipStatus,
    WorkspaceRole,
)
from app.domain.workspaces.settings import WorkspaceSettings, WorkspaceVisibility
from app.domain.workspaces.status import WorkspaceStatus
from app.domain.workspaces.workspace import Workspace

__all__ = [
    "DuplicateWorkspaceMember",
    "InvalidWorkspaceState",
    "OwnerCannotBeRemoved",
    "Workspace",
    "WorkspaceAlreadyExists",
    "WorkspaceArchived",
    "WorkspaceCreated",
    "WorkspaceMemberAdded",
    "WorkspaceMemberRemoved",
    "WorkspaceMembership",
    "WorkspaceMembershipStatus",
    "WorkspaceOwnerChanged",
    "WorkspaceRenamed",
    "WorkspaceRole",
    "WorkspaceSettings",
    "WorkspaceSettingsChanged",
    "WorkspaceStatus",
    "WorkspaceVisibility",
]
