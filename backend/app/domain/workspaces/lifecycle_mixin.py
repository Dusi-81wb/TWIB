"""Workspace lifecycle mixin."""

import typing
from typing import TYPE_CHECKING, Any

from app.domain.workspaces.events import WorkspaceArchived as WorkspaceArchivedEvent
from app.domain.workspaces.exceptions import (
    InvalidWorkspaceState,
    WorkspaceArchived as WorkspaceArchivedError,
)
from app.domain.workspaces.status import WorkspaceStatus
from app.domain.value_objects import UuidIdentity

class WorkspaceLifecycleMixin:
    """Mixin for workspace lifecycle methods."""

    def archive(self: Any) -> None:
        """Archive the workspace.

        An archived workspace cannot be modified until it is restored.

        Raises:
            InvalidWorkspaceState: When the workspace is deleted.
            WorkspaceArchived: When the workspace is already archived.
        """
        self._assert_not_deleted()
        if self._status is WorkspaceStatus.ARCHIVED:
            raise WorkspaceArchivedError(
                f"Workspace {self._workspace_id} is already archived"
            )
        self._status = WorkspaceStatus.ARCHIVED
        self._touch()
        self.record_event(WorkspaceArchivedEvent(workspace_id=self._workspace_id))

    def restore(self: Any) -> None:
        """Restore an archived workspace to the active state.

        Raises:
            InvalidWorkspaceState: When the workspace is not currently
                archived.
        """
        if self._status is not WorkspaceStatus.ARCHIVED:
            raise InvalidWorkspaceState(
                f"Workspace {self._workspace_id} is not archived, cannot restore"
            )
        self._status = WorkspaceStatus.ACTIVE
        self._touch()

    def activate(self: Any) -> None:
        """Activate the workspace.

        A suspended workspace becomes active.

        Raises:
            InvalidWorkspaceState: When the workspace is already active or
                deleted.
            WorkspaceArchived: When the workspace is archived; restore it
                first.
        """
        self._assert_not_deleted()
        if self._status is WorkspaceStatus.ACTIVE:
            raise InvalidWorkspaceState(
                f"Workspace {self._workspace_id} is already active"
            )
        if self._status is WorkspaceStatus.ARCHIVED:
            raise WorkspaceArchivedError(
                f"Workspace {self._workspace_id} is archived; restore it first"
            )
        self._status = WorkspaceStatus.ACTIVE
        self._touch()

    def suspend(self: Any) -> None:
        """Suspend the workspace.

        An active workspace becomes suspended.

        Raises:
            InvalidWorkspaceState: When the workspace is already suspended or
                deleted.
            WorkspaceArchived: When the workspace is archived.
        """
        self._assert_not_deleted()
        if self._status is WorkspaceStatus.SUSPENDED:
            raise InvalidWorkspaceState(
                f"Workspace {self._workspace_id} is already suspended"
            )
        if self._status is WorkspaceStatus.ARCHIVED:
            raise WorkspaceArchivedError(
                f"Archived workspace {self._workspace_id} cannot be suspended"
            )
        self._status = WorkspaceStatus.SUSPENDED
        self._touch()


if TYPE_CHECKING:
    from app.domain.workspaces.workspace import Workspace
