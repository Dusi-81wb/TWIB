"""Workspace aggregate root.

:class:`Workspace` is the collaboration boundary inside an organization: all
workflows, AI agents, documents, prompts, knowledge bases, API keys, and
executions belong to a workspace. It is an aggregate root built from the
Phase 2.2 value objects (:class:`UuidIdentity`, :class:`Name`,
:class:`Slug`, :class:`Description`, :class:`Timestamp`, :class:`Metadata`,
:class:`Version`), the domain enums (:class:`WorkspaceStatus`,
:class:`WorkspaceSettings`), and a collection of immutable
:class:`WorkspaceMembership` domain objects.

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
from app.domain.value_objects import (
    Description,
    Metadata,
    Name,
    Slug,
    Timestamp,
    UuidIdentity,
    Version,
)
from app.domain.workspaces.events import (
    WorkspaceArchived as WorkspaceArchivedEvent,
)
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
)
from app.domain.workspaces.exceptions import (
    WorkspaceArchived as WorkspaceArchivedError,
)
from app.domain.workspaces.membership import (
    WorkspaceMembership,
    WorkspaceMembershipStatus,
    WorkspaceRole,
)
from app.domain.workspaces.lifecycle_mixin import WorkspaceLifecycleMixin
from app.domain.workspaces.membership_mixin import WorkspaceMembershipMixin
from app.domain.workspaces.settings import WorkspaceSettings
from app.domain.workspaces.status import WorkspaceStatus


class Workspace(WorkspaceMembershipMixin, WorkspaceLifecycleMixin, AggregateRoot[uuid.UUID]):
    """A workspace, the collaboration boundary inside an organization.

    The workspace is an aggregate root whose state is entirely built from
    immutable value objects, enums, and immutable memberships and is exposed
    through read-only properties. All state changes go through domain methods
    that enforce the workspace business rules, record domain events, and bump
    the optimistic-locking version.

    Attributes:
        workspace_id: The stable UUID identity of the workspace.
        organization_id: The identity of the parent organization.
        name: The workspace's name.
        slug: The workspace's URL-friendly slug.
        description: The workspace's free-text description.
        owner_id: The identity of the workspace owner.
        created_at: When the workspace was created (UTC).
        updated_at: When the workspace was last changed (UTC).
        status: The current lifecycle state of the workspace.
        settings: The workspace configuration.
        metadata: The workspace's key/value metadata map.
        version: The optimistic-locking version of the aggregate.
        members: The current memberships of the workspace.
    """

    _workspace_id: UuidIdentity
    _organization_id: UuidIdentity
    _name: Name
    _slug: Slug
    _description: Description
    _owner_id: UuidIdentity
    _created_at: Timestamp
    _updated_at: Timestamp
    _status: WorkspaceStatus
    _settings: WorkspaceSettings
    _metadata: Metadata
    _version: Version
    _members: dict[UuidIdentity, WorkspaceMembership]

    def __init__(
        self,
        workspace_id: UuidIdentity,
        organization_id: UuidIdentity,
        name: Name,
        slug: Slug,
        description: Description,
        owner_id: UuidIdentity,
        status: WorkspaceStatus = WorkspaceStatus.ACTIVE,
        settings: WorkspaceSettings | None = None,
        created_at: Timestamp | None = None,
        updated_at: Timestamp | None = None,
        metadata: Metadata | None = None,
        version: Version | None = None,
    ) -> None:
        """Initialize a new workspace aggregate.

        The owner is implicitly added as an OWNER-role, active member.

        Args:
            workspace_id: The stable UUID identity of the workspace.
            organization_id: The identity of the parent organization.
            name: The workspace's name.
            slug: The workspace's URL-friendly slug.
            description: The workspace's free-text description.
            owner_id: The identity of the workspace owner.
            status: The initial lifecycle state (defaults to ACTIVE).
            settings: The workspace configuration (defaults to the defaults).
            created_at: The creation moment (defaults to now, UTC).
            updated_at: The last change moment (defaults to the creation
                moment).
            metadata: The workspace's metadata map (defaults to empty).
            version: The optimistic-locking version (defaults to 0.0.0).
        """
        super().__init__(Identity(workspace_id.value))
        now = created_at if created_at is not None else Timestamp.now()
        self._workspace_id = workspace_id
        self._organization_id = organization_id
        self._name = name
        self._slug = slug
        self._description = description
        self._owner_id = owner_id
        self._status = status
        self._settings = settings if settings is not None else WorkspaceSettings()
        self._created_at = now
        self._updated_at = updated_at if updated_at is not None else now
        self._metadata = metadata if metadata is not None else Metadata()
        self._version = version if version is not None else Version(0)
        self._members = {
            owner_id: WorkspaceMembership(
                user_id=owner_id,
                role=WorkspaceRole.OWNER,
                joined_at=now,
                status=WorkspaceMembershipStatus.ACTIVE,
                invitation_accepted=True,
            )
        }
        self.record_event(
            WorkspaceCreated(
                workspace_id=self._workspace_id,
                organization_id=self._organization_id,
            )
        )

    @property
    def workspace_id(self) -> UuidIdentity:
        """Return the stable UUID identity of the workspace."""
        return self._workspace_id

    @property
    def organization_id(self) -> UuidIdentity:
        """Return the identity of the parent organization."""
        return self._organization_id

    @property
    def name(self) -> Name:
        """Return the workspace's name."""
        return self._name

    @property
    def slug(self) -> Slug:
        """Return the workspace's URL-friendly slug."""
        return self._slug

    @property
    def description(self) -> Description:
        """Return the workspace's free-text description."""
        return self._description

    @property
    def owner_id(self) -> UuidIdentity:
        """Return the identity of the workspace owner."""
        return self._owner_id

    @property
    def created_at(self) -> Timestamp:
        """Return when the workspace was created (UTC)."""
        return self._created_at

    @property
    def updated_at(self) -> Timestamp:
        """Return when the workspace was last changed (UTC)."""
        return self._updated_at

    @property
    def status(self) -> WorkspaceStatus:
        """Return the current lifecycle state of the workspace."""
        return self._status

    @property
    def settings(self) -> WorkspaceSettings:
        """Return the workspace configuration."""
        return self._settings

    @property
    def metadata(self) -> Metadata:
        """Return the workspace's key/value metadata map."""
        return self._metadata

    @property
    def version(self) -> Version:
        """Return the optimistic-locking version of the aggregate."""
        return self._version

    @property
    def members(self) -> tuple[WorkspaceMembership, ...]:
        """Return the current memberships of the workspace."""
        return tuple(self._members.values())

    def get_member(self, user_id: UuidIdentity) -> WorkspaceMembership | None:
        """Return the membership of a user, if any.

        Args:
            user_id: The identity of the member.

        Returns:
            The membership, or ``None`` when the user is not a member.
        """
        return self._members.get(user_id)

    def rename(self, new_name: Name) -> None:
        """Change the workspace's name.

        A no-op when the new name equals the current one.

        Args:
            new_name: The new name.

        Raises:
            InvalidWorkspaceState: When the workspace is deleted.
            WorkspaceArchived: When the workspace is archived.
        """
        self._assert_mutable()
        if new_name == self._name:
            return
        previous = self._name
        self._name = new_name
        self._touch()
        self.record_event(
            WorkspaceRenamed(
                workspace_id=self._workspace_id,
                name=new_name,
                previous_name=previous,
            )
        )

    def change_slug(self, new_slug: Slug) -> None:
        """Change the workspace's URL-friendly slug.

        A no-op when the new slug equals the current one.

        Args:
            new_slug: The new slug.

        Raises:
            InvalidWorkspaceState: When the workspace is deleted.
            WorkspaceArchived: When the workspace is archived.
        """
        self._assert_mutable()
        if new_slug == self._slug:
            return
        self._slug = new_slug
        self._touch()

    def change_description(self, new_description: Description) -> None:
        """Change the workspace's free-text description.

        A no-op when the new description equals the current one.

        Args:
            new_description: The new description.

        Raises:
            InvalidWorkspaceState: When the workspace is deleted.
            WorkspaceArchived: When the workspace is archived.
        """
        self._assert_mutable()
        if new_description == self._description:
            return
        self._description = new_description
        self._touch()

    def update_settings(self, new_settings: WorkspaceSettings) -> None:
        """Replace the workspace's settings.

        A no-op when the new settings equal the current ones.

        Args:
            new_settings: The new settings.

        Raises:
            InvalidWorkspaceState: When the workspace is deleted.
            WorkspaceArchived: When the workspace is archived.
        """
        self._assert_mutable()
        if new_settings == self._settings:
            return
        previous = self._settings
        self._settings = new_settings
        self._touch()
        self.record_event(
            WorkspaceSettingsChanged(
                workspace_id=self._workspace_id,
                settings=new_settings,
                previous_settings=previous,
            )
        )

    def update_metadata(self, new_metadata: Metadata) -> None:
        """Replace the workspace's metadata map.

        A no-op when the new metadata equals the current one.

        Args:
            new_metadata: The new metadata map.

        Raises:
            InvalidWorkspaceState: When the workspace is deleted.
            WorkspaceArchived: When the workspace is archived.
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
            InvalidWorkspaceState: When the workspace is deleted.
            WorkspaceArchived: When the workspace is archived.
        """
        self._assert_mutable()
        self._bump_version()

    def _assert_not_deleted(self) -> None:
        """Raise when the workspace is deleted.

        Raises:
            InvalidWorkspaceState: When the workspace is deleted.
        """
        if self._status is WorkspaceStatus.DELETED:
            raise InvalidWorkspaceState(
                f"Deleted workspace {self._workspace_id} cannot be modified"
            )

    def _assert_mutable(self) -> None:
        """Raise when the workspace cannot be modified.

        Raises:
            InvalidWorkspaceState: When the workspace is deleted.
            WorkspaceArchived: When the workspace is archived.
        """
        self._assert_not_deleted()
        if self._status is WorkspaceStatus.ARCHIVED:
            raise WorkspaceArchivedError(
                f"Archived workspace {self._workspace_id} cannot be modified"
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
