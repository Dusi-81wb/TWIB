"""Organization membership management mixin."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.organizations.events import MemberAdded, MemberRemoved, OwnerChanged
from app.domain.organizations.exceptions import (
    DuplicateMember,
    InvalidOrganizationState,
    MembershipAlreadyExists,
    OwnerCannotBeRemoved,
)
from app.domain.organizations.membership import MembershipStatus, OrganizationMembership
from app.domain.users.role import UserRole
from app.domain.value_objects import Timestamp, UuidIdentity

if TYPE_CHECKING:
    from app.domain.organizations.organization import Organization


class OrganizationMemberMixin:
    """Mixin for organization member management."""

    @property
    def members(self: Organization) -> tuple[OrganizationMembership, ...]:
        """Return the current memberships of the organization."""
        return tuple(self._members.values())

    def get_member(self: Organization, user_id: UuidIdentity) -> OrganizationMembership | None:
        """Return the membership of a user, if any.

        Args:
            user_id: The identity of the member.

        Returns:
            The membership, or ``None`` when the user is not a member.
        """
        return self._members.get(user_id)

    def add_member(
        self: Organization, user_id: UuidIdentity, role: UserRole = UserRole.MEMBER
    ) -> None:
        """Add an active member to the organization.

        The owner is added automatically at construction, so the owner should
        not be added again.

        Args:
            user_id: The identity of the member to add.
            role: The role the member will hold (defaults to MEMBER).

        Raises:
            InvalidOrganizationState: When the organization is deleted.
            OrganizationArchived: When the organization is archived.
            DuplicateMember: When the user is already an active member.
            MembershipAlreadyExists: When a pending membership already exists
                for the user.
        """
        self._assert_mutable()
        existing = self._members.get(user_id)
        if existing is not None:
            if existing.status is MembershipStatus.ACTIVE:
                raise DuplicateMember(
                    f"User {user_id} is already an active member of organization "
                    f"{self._organization_id}"
                )
            raise MembershipAlreadyExists(
                f"A pending membership already exists for user {user_id}"
            )
        self._members[user_id] = OrganizationMembership(
            user_id=user_id,
            role=role,
            joined_at=Timestamp.now(),
            status=MembershipStatus.ACTIVE,
            invitation_accepted=True,
        )
        self._touch()
        self.record_event(
            MemberAdded(
                organization_id=self._organization_id,
                user_id=user_id,
                role=role,
            )
        )

    def remove_member(self: Organization, user_id: UuidIdentity) -> None:
        """Remove a member from the organization.

        The owner cannot be removed; transfer ownership first.

        Args:
            user_id: The identity of the member to remove.

        Raises:
            InvalidOrganizationState: When the organization is deleted or the
                user is not a member.
            OrganizationArchived: When the organization is archived.
            OwnerCannotBeRemoved: When the user is the organization owner.
        """
        self._assert_mutable()
        if user_id == self._owner_id:
            raise OwnerCannotBeRemoved(
                f"Owner user {user_id} cannot be removed from organization "
                f"{self._organization_id}; transfer ownership first"
            )
        if user_id not in self._members:
            raise InvalidOrganizationState(
                f"User {user_id} is not a member of organization "
                f"{self._organization_id}"
            )
        del self._members[user_id]
        self._touch()
        self.record_event(
            MemberRemoved(organization_id=self._organization_id, user_id=user_id)
        )

    def change_owner(self: Organization, new_owner_id: UuidIdentity) -> None:
        """Transfer ownership to an existing member.

        The new owner's membership role becomes OWNER and the previous owner's
        membership role becomes ADMIN.

        Args:
            new_owner_id: The identity of the new owner.

        Raises:
            InvalidOrganizationState: When the organization is deleted or the
                user is not a member.
            OrganizationArchived: When the organization is archived.
        """
        self._assert_mutable()
        if new_owner_id not in self._members:
            raise InvalidOrganizationState(
                f"User {new_owner_id} is not a member and cannot become the owner"
            )
        if new_owner_id == self._owner_id:
            return
        previous_owner = self._owner_id
        self._owner_id = new_owner_id
        self._change_member_role(new_owner_id, UserRole.OWNER)
        self._change_member_role(previous_owner, UserRole.ADMIN)
        self._touch()
        self.record_event(
            OwnerChanged(
                organization_id=self._organization_id,
                owner_id=new_owner_id,
                previous_owner_id=previous_owner,
            )
        )

    def _change_member_role(self: Organization, user_id: UuidIdentity, role: UserRole) -> None:
        """Replace a member's role while preserving the rest of the membership."""
        membership = self._members[user_id]
        self._members[user_id] = OrganizationMembership(
            user_id=membership.user_id,
            role=role,
            joined_at=membership.joined_at,
            status=membership.status,
            invitation_accepted=membership.invitation_accepted,
        )
