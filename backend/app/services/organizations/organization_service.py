"""Organization application service.

Orchestrates organization management operations using the Unit of Work,
repositories, and domain aggregate methods. No direct database access;
all persistence goes through the repository layer.
"""

from __future__ import annotations

import uuid

from app.domain.exceptions import BusinessRuleViolation, EntityNotFound
from app.domain.organizations.organization import Organization
from app.domain.organizations.plan import SubscriptionPlan
from app.domain.organizations.status import OrganizationStatus
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.value_objects import Name, Slug, UuidIdentity


class OrganizationService:
    """Application service managing organization lifecycle operations.

    All methods interact with the persistence layer exclusively through
    the Unit of Work and its repositories.

    Attributes:
        _uow: Unit of Work for repository access.
    """

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        """Initialize the organization service.

        Args:
            unit_of_work: Unit of Work for repository access.
        """
        self._uow = unit_of_work

    async def create_organization(
        self,
        name: str,
        owner_id: str,
        slug: str | None = None,
    ) -> Organization:
        """Create a new organization aggregate and persist it.

        Args:
            name: Organization name string.
            owner_id: UUID string of the owner user.
            slug: Optional custom slug string.

        Returns:
            The created Organization domain aggregate.

        Raises:
            BusinessRuleViolation: If slug is invalid or already taken.
        """
        try:
            o_uuid = uuid.uuid4()
            u_uuid = uuid.UUID(owner_id)
            name_vo = Name(name)
            slug_str = slug if slug else name.lower().replace(" ", "-")
            slug_vo = Slug(slug_str)
        except ValueError as err:
            raise BusinessRuleViolation(str(err)) from err

        async with self._uow as uow:
            if await uow.organizations.exists_by_slug(slug_vo):
                raise BusinessRuleViolation(
                    f"Organization with slug '{slug_vo.value}' already exists"
                )

            org = Organization(
                organization_id=UuidIdentity(o_uuid),
                name=name_vo,
                slug=slug_vo,
                owner_id=UuidIdentity(u_uuid),
                status=OrganizationStatus.ACTIVE,
            )
            await uow.organizations.save(org)
            await uow.commit()
        return org

    async def get_organization(self, organization_id: str) -> Organization:
        """Retrieve an organization by ID.

        Args:
            organization_id: UUID string of the target organization.

        Returns:
            The Organization domain aggregate.

        Raises:
            EntityNotFound: If organization does not exist.
        """
        return await self._find_organization_or_raise(organization_id)

    async def list_organizations(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Organization], int]:
        """List organizations with pagination.

        Args:
            limit: Maximum number of organizations to return.
            offset: Number of organizations to skip.

        Returns:
            Tuple of (list of Organization aggregates, total count).
        """
        async with self._uow as uow:
            orgs = await uow.organizations.find_all(limit=limit, offset=offset)
            total = await uow.organizations.count()
        return orgs, total

    async def update_organization(
        self,
        organization_id: str,
        name: str | None = None,
        slug: str | None = None,
        subscription_plan: str | None = None,
        status: str | None = None,
    ) -> Organization:
        """Update an organization's details, plan, or status.

        Args:
            organization_id: UUID string of the target organization.
            name: Optional new organization name.
            slug: Optional new URL-friendly slug.
            subscription_plan: Optional new subscription plan string.
            status: Optional new status string.

        Returns:
            The updated Organization domain aggregate.

        Raises:
            EntityNotFound: If organization does not exist.
            BusinessRuleViolation: If a domain rule is violated.
        """
        async with self._uow as uow:
            try:
                org_uuid = uuid.UUID(organization_id)
            except ValueError as err:
                raise EntityNotFound(
                    f"Organization '{organization_id}' not found"
                ) from err

            org = await uow.organizations.find_by_id(UuidIdentity(org_uuid))
            if org is None:
                raise EntityNotFound(f"Organization '{organization_id}' not found")

            if name is not None:
                org.rename(Name(name))

            if slug is not None:
                new_slug = Slug(slug)
                if new_slug != org.slug and await uow.organizations.exists_by_slug(
                    new_slug
                ):
                    raise BusinessRuleViolation(
                        f"Organization with slug '{new_slug.value}' already exists"
                    )
                org.change_slug(new_slug)

            if subscription_plan is not None:
                try:
                    plan_enum = SubscriptionPlan(subscription_plan)
                except ValueError as err:
                    raise BusinessRuleViolation(
                        f"Invalid subscription plan: '{subscription_plan}'"
                    ) from err
                org.change_plan(plan_enum)

            if status is not None:
                self._apply_status_change(org, status)

            await uow.organizations.save(org)
            await uow.commit()
        return org

    async def delete_organization(self, organization_id: str) -> Organization:
        """Soft-delete an organization.

        Args:
            organization_id: UUID string of the target organization.

        Returns:
            The deleted Organization domain aggregate.

        Raises:
            EntityNotFound: If organization does not exist.
            BusinessRuleViolation: If a domain rule is violated.
        """
        async with self._uow as uow:
            try:
                org_uuid = uuid.UUID(organization_id)
            except ValueError as err:
                raise EntityNotFound(
                    f"Organization '{organization_id}' not found"
                ) from err

            org = await uow.organizations.find_by_id(UuidIdentity(org_uuid))
            if org is None:
                raise EntityNotFound(f"Organization '{organization_id}' not found")

            org.archive()
            await uow.organizations.save(org)
            await uow.commit()
        return org

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _find_organization_or_raise(self, organization_id: str) -> Organization:
        """Find an organization by ID or raise EntityNotFound.

        Args:
            organization_id: UUID string of the target organization.

        Returns:
            The Organization domain aggregate.

        Raises:
            EntityNotFound: If organization does not exist.
        """
        try:
            oid = uuid.UUID(organization_id)
        except ValueError as err:
            raise EntityNotFound(f"Organization '{organization_id}' not found") from err

        async with self._uow as uow:
            org = await uow.organizations.find_by_id(UuidIdentity(oid))

        if org is None:
            raise EntityNotFound(f"Organization '{organization_id}' not found")
        return org

    @staticmethod
    def _apply_status_change(org: Organization, status: str) -> None:
        """Apply status transition via domain methods.

        Args:
            org: Target Organization aggregate.
            status: Target status string.

        Raises:
            BusinessRuleViolation: If status string is invalid.
        """
        try:
            target = OrganizationStatus(status)
        except ValueError as err:
            raise BusinessRuleViolation(f"Invalid status: '{status}'") from err

        transitions = {
            OrganizationStatus.ACTIVE: org.activate,
            OrganizationStatus.SUSPENDED: org.suspend,
            OrganizationStatus.ARCHIVED: org.archive,
        }

        handler = transitions.get(target)
        if handler is None:
            raise BusinessRuleViolation(
                f"Cannot transition organization to status '{status}'"
            )
        handler()
