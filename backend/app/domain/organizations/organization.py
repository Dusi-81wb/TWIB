"""Organization aggregate root.

:class:`Organization` is the tenant boundary of TWIB: everything in the
platform belongs to an organization. It is an aggregate root built from the
Phase 2.2 value objects (:class:`UuidIdentity`, :class:`Name`,
:class:`Slug`, :class:`Timestamp`, :class:`Metadata`, :class:`Version`), the
domain enums (:class:`OrganizationStatus`, :class:`SubscriptionPlan`), and a
collection of immutable :class:`OrganizationMembership` domain objects.

The aggregate exposes its state through read-only properties only, so callers
can never mutate it directly. Every state change happens through a domain
method that validates the operation, records the appropriate domain event, and
bumps the version (optimistic locking).

This module is pure Python: no FastAPI, Pydantic, SQLAlchemy, repository, or
authentication.
"""

from __future__ import annotations

import uuid

from app.domain.aggregate import AggregateRoot
from app.domain.entity import Identity
from app.domain.organizations.events import (
    MemberAdded,
    MemberRemoved,
    OrganizationActivated,
    OrganizationCreated,
    OrganizationRenamed,
    OrganizationSuspended,
    OwnerChanged,
    PlanChanged,
)
from app.domain.organizations.exceptions import (
    DuplicateMember,
    InvalidOrganizationState,
    MembershipAlreadyExists,
    OrganizationArchived,
    OwnerCannotBeRemoved,
)
from app.domain.organizations.membership import (
    MembershipStatus,
    OrganizationMembership,
)
from app.domain.organizations.plan import SubscriptionPlan
from app.domain.organizations.status import OrganizationStatus
from app.domain.users.role import UserRole
from app.domain.value_objects import (
    Metadata,
    Name,
    Slug,
    Timestamp,
    UuidIdentity,
    Version,
)


class Organization(AggregateRoot[uuid.UUID]):
    """An organization, the tenant boundary of TWIB.

    The organization is an aggregate root whose state is entirely built from
    immutable value objects, enums, and immutable memberships and is exposed
    through read-only properties. All state changes go through domain methods
    that enforce the organization business rules, record domain events, and
    bump the optimistic-locking version.

    Attributes:
        organization_id: The stable UUID identity of the organization.
        name: The organization's name.
        slug: The organization's URL-friendly slug.
        owner_id: The identity of the organization owner.
        created_at: When the organization was created (UTC).
        updated_at: When the organization was last changed (UTC).
        status: The current lifecycle state of the organization.
        subscription_plan: The subscription plan the organization is on.
        metadata: The organization's key/value metadata map.
        version: The optimistic-locking version of the aggregate.
        members: The current memberships of the organization.
    """

    _organization_id: UuidIdentity
    _name: Name
    _slug: Slug
    _owner_id: UuidIdentity
    _created_at: Timestamp
    _updated_at: Timestamp
    _status: OrganizationStatus
    _subscription_plan: SubscriptionPlan
    _metadata: Metadata
    _version: Version
    _members: dict[UuidIdentity, OrganizationMembership]

    def __init__(
        self,
        organization_id: UuidIdentity,
        name: Name,
        slug: Slug,
        owner_id: UuidIdentity,
        status: OrganizationStatus = OrganizationStatus.PENDING,
        subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE,
        created_at: Timestamp | None = None,
        updated_at: Timestamp | None = None,
        metadata: Metadata | None = None,
        version: Version | None = None,
    ) -> None:
        """Initialize a new organization aggregate.

        The owner is implicitly added as an OWNER-role, active member.

        Args:
            organization_id: The stable UUID identity of the organization.
            name: The organization's name.
            slug: The organization's URL-friendly slug.
            owner_id: The identity of the organization owner.
            status: The initial lifecycle state (defaults to PENDING).
            subscription_plan: The subscription plan (defaults to FREE).
            created_at: The creation moment (defaults to now, UTC).
            updated_at: The last change moment (defaults to the creation
                moment).
            metadata: The organization's metadata map (defaults to empty).
            version: The optimistic-locking version (defaults to 0.0.0).
        """
        super().__init__(Identity(organization_id.value))
        now = created_at if created_at is not None else Timestamp.now()
        self._organization_id = organization_id
        self._name = name
        self._slug = slug
        self._owner_id = owner_id
        self._status = status
        self._subscription_plan = subscription_plan
        self._created_at = now
        self._updated_at = updated_at if updated_at is not None else now
        self._metadata = metadata if metadata is not None else Metadata()
        self._version = version if version is not None else Version(0)
        self._members = {
            owner_id: OrganizationMembership(
                user_id=owner_id,
                role=UserRole.OWNER,
                joined_at=now,
                status=MembershipStatus.ACTIVE,
                invitation_accepted=True,
            )
        }
        self.record_event(OrganizationCreated(organization_id=self._organization_id))

    @property
    def organization_id(self) -> UuidIdentity:
        """Return the stable UUID identity of the organization."""
        return self._organization_id

    @property
    def name(self) -> Name:
        """Return the organization's name."""
        return self._name

    @property
    def slug(self) -> Slug:
        """Return the organization's URL-friendly slug."""
        return self._slug

    @property
    def owner_id(self) -> UuidIdentity:
        """Return the identity of the organization owner."""
        return self._owner_id

    @property
    def created_at(self) -> Timestamp:
        """Return when the organization was created (UTC)."""
        return self._created_at

    @property
    def updated_at(self) -> Timestamp:
        """Return when the organization was last changed (UTC)."""
        return self._updated_at

    @property
    def status(self) -> OrganizationStatus:
        """Return the current lifecycle state of the organization."""
        return self._status

    @property
    def subscription_plan(self) -> SubscriptionPlan:
        """Return the subscription plan the organization is on."""
        return self._subscription_plan

    @property
    def metadata(self) -> Metadata:
        """Return the organization's key/value metadata map."""
        return self._metadata

    @property
    def version(self) -> Version:
        """Return the optimistic-locking version of the aggregate."""
        return self._version

    @property
    def members(self) -> tuple[OrganizationMembership, ...]:
        """Return the current memberships of the organization."""
        return tuple(self._members.values())

    def get_member(self, user_id: UuidIdentity) -> OrganizationMembership | None:
        """Return the membership of a user, if any.

        Args:
            user_id: The identity of the member.

        Returns:
            The membership, or ``None`` when the user is not a member.
        """
        return self._members.get(user_id)

    def rename(self, new_name: Name) -> None:
        """Change the organization's name.

        A no-op when the new name equals the current one.

        Args:
            new_name: The new name.

        Raises:
            InvalidOrganizationState: When the organization is deleted.
            OrganizationArchived: When the organization is archived.
        """
        self._assert_mutable()
        if new_name == self._name:
            return
        previous = self._name
        self._name = new_name
        self._touch()
        self.record_event(
            OrganizationRenamed(
                organization_id=self._organization_id,
                name=new_name,
                previous_name=previous,
            )
        )

    def change_slug(self, new_slug: Slug) -> None:
        """Change the organization's URL-friendly slug.

        A no-op when the new slug equals the current one.

        Args:
            new_slug: The new slug.

        Raises:
            InvalidOrganizationState: When the organization is deleted.
            OrganizationArchived: When the organization is archived.
        """
        self._assert_mutable()
        if new_slug == self._slug:
            return
        self._slug = new_slug
        self._touch()

    def change_plan(self, new_plan: SubscriptionPlan) -> None:
        """Change the organization's subscription plan.

        A no-op when the new plan equals the current one.

        Args:
            new_plan: The new subscription plan.

        Raises:
            InvalidOrganizationState: When the organization is deleted.
            OrganizationArchived: When the organization is archived.
        """
        self._assert_mutable()
        if new_plan == self._subscription_plan:
            return
        previous = self._subscription_plan
        self._subscription_plan = new_plan
        self._touch()
        self.record_event(
            PlanChanged(
                organization_id=self._organization_id,
                plan=new_plan,
                previous_plan=previous,
            )
        )

    def activate(self) -> None:
        """Activate the organization.

        Pending and suspended organizations become active.

        Raises:
            InvalidOrganizationState: When the organization is already active
                or deleted.
            OrganizationArchived: When the organization is archived; restore
                it first.
        """
        self._assert_not_deleted()
        if self._status is OrganizationStatus.ACTIVE:
            raise InvalidOrganizationState(
                f"Organization {self._organization_id} is already active"
            )
        if self._status is OrganizationStatus.ARCHIVED:
            raise OrganizationArchived(
                f"Organization {self._organization_id} is archived; restore it first"
            )
        self._status = OrganizationStatus.ACTIVE
        self._touch()
        self.record_event(OrganizationActivated(organization_id=self._organization_id))

    def suspend(self) -> None:
        """Suspend the organization.

        Pending and active organizations become suspended.

        Raises:
            InvalidOrganizationState: When the organization is already
                suspended or deleted.
            OrganizationArchived: When the organization is archived.
        """
        self._assert_not_deleted()
        if self._status is OrganizationStatus.SUSPENDED:
            raise InvalidOrganizationState(
                f"Organization {self._organization_id} is already suspended"
            )
        if self._status is OrganizationStatus.ARCHIVED:
            raise OrganizationArchived(
                f"Archived organization {self._organization_id} cannot be suspended"
            )
        self._status = OrganizationStatus.SUSPENDED
        self._touch()
        self.record_event(OrganizationSuspended(organization_id=self._organization_id))

    def archive(self) -> None:
        """Archive the organization.

        An archived organization cannot be modified until it is restored.

        Raises:
            InvalidOrganizationState: When the organization is deleted.
            OrganizationArchived: When the organization is already archived.
        """
        self._assert_not_deleted()
        if self._status is OrganizationStatus.ARCHIVED:
            raise OrganizationArchived(
                f"Organization {self._organization_id} is already archived"
            )
        self._status = OrganizationStatus.ARCHIVED
        self._touch()

    def restore(self) -> None:
        """Restore an archived organization to the active state.

        Raises:
            InvalidOrganizationState: When the organization is not currently
                archived.
        """
        if self._status is not OrganizationStatus.ARCHIVED:
            raise InvalidOrganizationState(
                f"Organization {self._organization_id} is not archived, cannot restore"
            )
        self._status = OrganizationStatus.ACTIVE
        self._touch()

    def add_member(
        self, user_id: UuidIdentity, role: UserRole = UserRole.MEMBER
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

    def remove_member(self, user_id: UuidIdentity) -> None:
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

    def change_owner(self, new_owner_id: UuidIdentity) -> None:
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

    def update_metadata(self, new_metadata: Metadata) -> None:
        """Replace the organization's metadata map.

        A no-op when the new metadata equals the current one.

        Args:
            new_metadata: The new metadata map.

        Raises:
            InvalidOrganizationState: When the organization is deleted.
            OrganizationArchived: When the organization is archived.
        """
        self._assert_mutable()
        if new_metadata == self._metadata:
            return
        self._metadata = new_metadata
        self._touch()

    def increment_version(self) -> None:
        """Bump the optimistic-locking version by one patch.

        Domain methods bump the version automatically; call this directly only
        when an out-of-band change was applied to the aggregate.

        Raises:
            InvalidOrganizationState: When the organization is deleted.
            OrganizationArchived: When the organization is archived.
        """
        self._assert_mutable()
        self._bump_version()

    def _change_member_role(self, user_id: UuidIdentity, role: UserRole) -> None:
        """Replace a member's role while preserving the rest of the membership."""
        membership = self._members[user_id]
        self._members[user_id] = OrganizationMembership(
            user_id=membership.user_id,
            role=role,
            joined_at=membership.joined_at,
            status=membership.status,
            invitation_accepted=membership.invitation_accepted,
        )

    def _assert_not_deleted(self) -> None:
        """Raise when the organization is deleted.

        Raises:
            InvalidOrganizationState: When the organization is deleted.
        """
        if self._status is OrganizationStatus.DELETED:
            raise InvalidOrganizationState(
                f"Deleted organization {self._organization_id} cannot be modified"
            )

    def _assert_mutable(self) -> None:
        """Raise when the organization cannot be modified.

        Raises:
            InvalidOrganizationState: When the organization is deleted.
            OrganizationArchived: When the organization is archived.
        """
        self._assert_not_deleted()
        if self._status is OrganizationStatus.ARCHIVED:
            raise OrganizationArchived(
                f"Archived organization {self._organization_id} cannot be modified"
            )

    def _touch(self) -> None:
        """Refresh the update timestamp and bump the version."""
        self._updated_at = Timestamp.now()
        self._bump_version()

    def _bump_version(self) -> None:
        """Increment the optimistic-locking version by one patch."""
        self._version = Version(
            self._version.major,
            self._version.minor,
            self._version.patch + 1,
        )
