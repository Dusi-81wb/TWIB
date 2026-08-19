"""Organization repository interface.

The persistence contract for the
:class:`~app.domain.organizations.organization.Organization` aggregate.
Application services depend on this protocol, never on a concrete database
implementation, so persistence can be swapped without touching business logic
(Clean Architecture / Repository Pattern).

Only the interface is declared here. There is no SQLAlchemy, database, or
infrastructure code in the domain layer.
"""

from __future__ import annotations

from typing import Protocol

from app.domain.organizations.organization import Organization
from app.domain.value_objects import Slug, UuidIdentity


class OrganizationRepository(Protocol):
    """Persistence contract for the :class:`Organization` aggregate.

    This repository exposes the business-oriented queries the application
    needs (looking up an organization by slug or owner, checking slug
    uniqueness, and persisting or deleting an organization) instead of an
    unrestricted generic CRUD surface.
    """

    async def find_by_id(self, id_: UuidIdentity) -> Organization | None:
        """Find an organization by identity.

        Args:
            id_: The identity to look up.

        Returns:
            The organization aggregate, or None if not found.
        """
        ...

    async def find_by_slug(self, slug: Slug) -> Organization | None:
        """Find an organization by its URL-friendly slug.

        Args:
            slug: The slug to look up.

        Returns:
            The organization, or ``None`` when no organization has that slug.
        """
        ...

    async def find_by_owner(self, owner_id: UuidIdentity) -> list[Organization]:
        """Find every organization owned by a user.

        Args:
            owner_id: The identity of the owning user.

        Returns:
            The organizations owned by the user (possibly empty).
        """
        ...

    async def exists_by_slug(self, slug: Slug) -> bool:
        """Return whether an organization with the slug exists.

        Args:
            slug: The slug to check.

        Returns:
            True when an organization already has that slug.
        """
        ...

    async def find_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Organization]:
        """Return a paginated list of organizations.

        Args:
            limit: Maximum number of organizations to return.
            offset: Number of organizations to skip.

        Returns:
            A list of Organization aggregates.
        """
        ...

    async def count(self) -> int:
        """Return the total number of organizations.

        Returns:
            The total count of organizations in the repository.
        """
        ...

    async def save(self, organization: Organization) -> None:
        """Persist an organization, inserting or updating it as needed.

        Args:
            organization: The organization aggregate to persist.
        """
        ...

    async def delete(self, id_: UuidIdentity) -> None:
        """Delete the organization with the identity.

        Args:
            id_: The identity of the organization to delete.
        """
        ...
