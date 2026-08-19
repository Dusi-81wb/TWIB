"""Workspace domain events.

These events record the meaningful things that happen to a workspace
aggregate. They subclass :class:`~app.domain.event.DomainEvent`, so every
occurrence carries a unique ``event_id`` and a UTC ``occurred_at`` timestamp.

The aggregate only records events through
:meth:`~app.domain.aggregate.AggregateRoot.record_event`; publishing belongs
to outer layers. No event bus exists in this phase.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.event import DomainEvent
from app.domain.value_objects import Name, UuidIdentity
from app.domain.workspaces.membership import WorkspaceRole
from app.domain.workspaces.settings import WorkspaceSettings


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class WorkspaceCreated(DomainEvent):
    """Recorded when a workspace aggregate is created."""

    workspace_id: UuidIdentity
    organization_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class WorkspaceArchived(DomainEvent):
    """Recorded when a workspace is archived."""

    workspace_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class WorkspaceRenamed(DomainEvent):
    """Recorded when a workspace is renamed."""

    workspace_id: UuidIdentity
    name: Name
    previous_name: Name


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class WorkspaceOwnerChanged(DomainEvent):
    """Recorded when the workspace owner changes."""

    workspace_id: UuidIdentity
    owner_id: UuidIdentity
    previous_owner_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class WorkspaceMemberAdded(DomainEvent):
    """Recorded when a member is added to a workspace."""

    workspace_id: UuidIdentity
    user_id: UuidIdentity
    role: WorkspaceRole


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class WorkspaceMemberRemoved(DomainEvent):
    """Recorded when a member is removed from a workspace."""

    workspace_id: UuidIdentity
    user_id: UuidIdentity


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class WorkspaceSettingsChanged(DomainEvent):
    """Recorded when the workspace settings change."""

    workspace_id: UuidIdentity
    settings: WorkspaceSettings
    previous_settings: WorkspaceSettings
