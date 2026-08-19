"""Workspace status enumeration.

A :class:`WorkspaceStatus` is the immutable, string-valued representation of
the lifecycle state of a workspace. The transitions between states are
enforced by the workspace aggregate's business rules.
"""

from __future__ import annotations

from enum import StrEnum


class WorkspaceStatus(StrEnum):
    """The lifecycle states a workspace can be in.

    Members:
        ACTIVE: The workspace is active and usable.
        ARCHIVED: The workspace was archived; it cannot be modified until
            restored.
        SUSPENDED: The workspace was temporarily suspended.
        DELETED: The workspace was deleted; this state is terminal.
    """

    ACTIVE = "active"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"
    DELETED = "deleted"
