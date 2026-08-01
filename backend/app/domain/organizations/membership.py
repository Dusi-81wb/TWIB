"""Organization membership domain object.

An :class:`OrganizationMembership` is an immutable representation of a user's
membership inside an organization. It is a domain object built from value
objects and enums; it carries no behaviour beyond its own validation. The
:class:`MembershipStatus` enumeration is also defined here because it belongs
to the membership concept.
"""

from __future__ import annotations

from enum import StrEnum

from app.domain.exceptions import InvalidValue
from app.domain.users.role import UserRole
from app.domain.value_object import ValueObject
from app.domain.value_objects import Timestamp, UuidIdentity


class MembershipStatus(StrEnum):
    """The states a membership can be in.

    Members:
        PENDING: The invitation was sent but has not been accepted yet.
        ACTIVE: The member is active in the organization.
        INACTIVE: The member is no longer active (for example removed).
    """

    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"


class OrganizationMembership(ValueObject):
    """An immutable membership of a user in an organization.

    A pending membership (invitation not yet accepted) is mutually exclusive
    with an accepted one, so the ``status`` and ``invitation_accepted`` fields
    are validated together at construction.

    Attributes:
        user_id: The identity of the member.
        role: The role the member holds in the organization.
        joined_at: When the membership started (UTC).
        status: The current membership state.
        invitation_accepted: Whether the invitation was accepted.
    """

    user_id: UuidIdentity
    role: UserRole
    joined_at: Timestamp
    status: MembershipStatus
    invitation_accepted: bool

    def __init__(
        self,
        user_id: UuidIdentity,
        role: UserRole,
        joined_at: Timestamp | None = None,
        status: MembershipStatus = MembershipStatus.ACTIVE,
        invitation_accepted: bool = True,
    ) -> None:
        """Initialize the membership.

        Args:
            user_id: The identity of the member.
            role: The role the member holds in the organization.
            joined_at: When the membership started (defaults to now, UTC).
            status: The membership state (defaults to ACTIVE).
            invitation_accepted: Whether the invitation was accepted
                (defaults to True).

        Raises:
            InvalidValue: When the status and the invitation-accepted flag
                are inconsistent.
        """
        if status is MembershipStatus.PENDING and invitation_accepted:
            raise InvalidValue(
                "A pending membership cannot have an accepted invitation"
            )
        if not invitation_accepted and status is not MembershipStatus.PENDING:
            raise InvalidValue(
                "A non-pending membership must have an accepted invitation"
            )
        object.__setattr__(self, "user_id", user_id)
        object.__setattr__(self, "role", role)
        object.__setattr__(
            self,
            "joined_at",
            joined_at if joined_at is not None else Timestamp.now(),
        )
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "invitation_accepted", invitation_accepted)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because memberships are immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")
