"""Workspace repository interface.

The persistence contract for the
:class:`~app.domain.workspaces.workspace.Workspace` aggregate. Application
services depend on this protocol, never on a concrete database implementation,
so persistence can be swapped without touching business logic (Clean
Architecture / Repository Pattern).

Only the interface is declared here. There is no SQLAlchemy, database, or
infrastructure code in the domain layer.
"""

from __future__ import annotations

from typing import Protocol

from app.domain.value_objects import Slug, UuidIdentity
from app.domain.workspaces.workspace import Workspace


class WorkspaceRepository(Protocol):
    """Persistence contract for the :class:`Workspace` aggregate.

    This repository exposes the business-oriented queries the application
    needs (looking up workspaces by slug, parent organization, or owner,
    checking slug uniqueness, and persisting or deleting a workspace) instead
    of an unrestricted generic CRUD surface. Workspace slugs are scoped to a
    parent organization, so slug lookups are organization-aware.
    """

    async def find_by_id(self, id_: UuidIdentity) -> Workspace | None:
        """Find a workspace by identity.

        Args:
            id_: The identity to look up.

        Returns:
            The workspace aggregate, or None if not found.
        """
        ...

    async def find_by_slug(
        self, organization_id: UuidIdentity, slug: Slug
    ) -> Workspace | None:
        """Find a workspace by its slug inside an organization.

        Args:
            organization_id: The identity of the parent organization.
            slug: The slug to look up.

        Returns:
            The workspace, or ``None`` when no workspace in that organization
            has the slug.
        """
        ...

    async def find_by_organization(
        self, organization_id: UuidIdentity
    ) -> list[Workspace]:
        """Find every workspace in an organization.

        Args:
            organization_id: The identity of the parent organization.

        Returns:
            The workspaces in the organization (possibly empty).
        """
        ...

    async def find_by_owner(self, owner_id: UuidIdentity) -> list[Workspace]:
        """Find every workspace owned by a user.

        Args:
            owner_id: The identity of the owning user.

        Returns:
            The workspaces owned by the user (possibly empty).
        """
        ...

    async def exists_by_slug(self, organization_id: UuidIdentity, slug: Slug) -> bool:
        """Return whether a workspace with the slug exists in an organization.

        Args:
            organization_id: The identity of the parent organization.
            slug: The slug to check.

        Returns:
            True when a workspace in that organization already has the slug.
        """
        ...

    async def find_all(
        self,
        limit: int = 50,
        offset: int = 0,
        organization_id: UuidIdentity | None = None,
    ) -> list[Workspace]:
        """Return a paginated list of workspaces.

        Args:
            limit: Maximum number of workspaces to return.
            offset: Number of workspaces to skip.
            organization_id: Optional organization filter.

        Returns:
            A list of Workspace aggregates.
        """
        ...

    async def count(self, organization_id: UuidIdentity | None = None) -> int:
        """Return the total number of workspaces.

        Args:
            organization_id: Optional organization filter.

        Returns:
            The total count of workspaces.
        """
        ...

    async def save(self, workspace: Workspace) -> None:
        """Persist a workspace, inserting or updating it as needed.

        Args:
            workspace: The workspace aggregate to persist.
        """
        ...

    async def delete(self, id_: UuidIdentity) -> None:
        """Delete the workspace with the identity.

        Args:
            id_: The identity of the workspace to delete.
        """
        ...
