"""Workspace membership mixin."""

import typing
from typing import TYPE_CHECKING, Any

from app.domain.value_objects import Timestamp, UuidIdentity
from app.domain.workspaces.events import (
    WorkspaceMemberAdded,
    WorkspaceMemberRemoved,
    WorkspaceOwnerChanged,
)
from app.domain.workspaces.exceptions import (
    DuplicateWorkspaceMember,
    InvalidWorkspaceState,
    OwnerCannotBeRemoved,
)
from app.domain.workspaces.membership import (
    WorkspaceMembership,
    WorkspaceMembershipStatus,
    WorkspaceRole,
)


class WorkspaceMembershipMixin:
    """Mixin for workspace membership methods."""

    def add_member(
        self: Any, user_id: UuidIdentity, role: WorkspaceRole = WorkspaceRole.VIEWER
    ) -> None:
        """Add an active member to the workspace.

        The owner is added automatically at construction, so the owner should
        not be added again.

        Args:
            user_id: The identity of the member to add.
            role: The role the member will hold (defaults to VIEWER).

        Raises:
            InvalidWorkspaceState: When the workspace is deleted.
            WorkspaceArchived: When the workspace is archived.
            DuplicateWorkspaceMember: When the user is already a member.
        """
        self._assert_mutable()
        if user_id in self._members:
            raise DuplicateWorkspaceMember(
                f"User {user_id} is already a member of workspace {self._workspace_id}"
            )
        self._members[user_id] = WorkspaceMembership(
            user_id=user_id,
            role=role,
            joined_at=Timestamp.now(),
            status=WorkspaceMembershipStatus.ACTIVE,
            invitation_accepted=True,
        )
        self._touch()
        self.record_event(
            WorkspaceMemberAdded(
                workspace_id=self._workspace_id,
                user_id=user_id,
                role=role,
            )
        )

    def remove_member(self: Any, user_id: UuidIdentity) -> None:
        """Remove a member from the workspace.

        The owner cannot be removed; transfer ownership first.

        Args:
            user_id: The identity of the member to remove.

        Raises:
            InvalidWorkspaceState: When the workspace is deleted or the user is
                not a member.
            WorkspaceArchived: When the workspace is archived.
            OwnerCannotBeRemoved: When the user is the workspace owner.
        """
        self._assert_mutable()
        if user_id == self._owner_id:
            raise OwnerCannotBeRemoved(
                f"Owner user {user_id} cannot be removed from workspace "
                f"{self._workspace_id}; transfer ownership first"
            )
        if user_id not in self._members:
            raise InvalidWorkspaceState(
                f"User {user_id} is not a member of workspace {self._workspace_id}"
            )
        del self._members[user_id]
        self._touch()
        self.record_event(
            WorkspaceMemberRemoved(workspace_id=self._workspace_id, user_id=user_id)
        )

    def change_owner(self: Any, new_owner_id: UuidIdentity) -> None:
        """Transfer ownership to an existing member.

        The new owner's membership role becomes OWNER and the previous owner's
        membership role becomes ADMIN.

        Args:
            new_owner_id: The identity of the new owner.

        Raises:
            InvalidWorkspaceState: When the workspace is deleted or the user is
                not a member.
            WorkspaceArchived: When the workspace is archived.
        """
        self._assert_mutable()
        if new_owner_id not in self._members:
            raise InvalidWorkspaceState(
                f"User {new_owner_id} is not a member and cannot become the owner"
            )
        if new_owner_id == self._owner_id:
            return
        previous_owner = self._owner_id
        self._owner_id = new_owner_id
        self._change_member_role(new_owner_id, WorkspaceRole.OWNER)
        self._change_member_role(previous_owner, WorkspaceRole.ADMIN)
        self._touch()
        self.record_event(
            WorkspaceOwnerChanged(
                workspace_id=self._workspace_id,
                owner_id=new_owner_id,
                previous_owner_id=previous_owner,
            )
        )

    def _change_member_role(self: Any, user_id: UuidIdentity, role: WorkspaceRole) -> None:
        """Replace a member's role while preserving the rest of the membership."""
        membership = self._members[user_id]
        self._members[user_id] = WorkspaceMembership(
            user_id=membership.user_id,
            role=role,
            joined_at=membership.joined_at,
            status=membership.status,
            invitation_accepted=membership.invitation_accepted,
        )


if TYPE_CHECKING:
    from app.domain.workspaces.workspace import Workspace
