"""SQLAlchemy Organization repository implementation.

This module implements
:class:`~app.domain.repositories.organization_repository.OrganizationRepository`
backed by SQLAlchemy 2.0 and
:class:`app.infrastructure.database.models.organization_model.OrganizationModel`.
It translates between the domain aggregate
:class:`app.domain.organizations.organization.Organization`
and the persistence layer.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.organizations.membership import (
    MembershipStatus,
    OrganizationMembership,
)
from app.domain.organizations.organization import Organization
from app.domain.organizations.plan import SubscriptionPlan
from app.domain.organizations.status import OrganizationStatus
from app.domain.repositories.organization_repository import OrganizationRepository
from app.domain.users.role import UserRole
from app.domain.value_objects import (
    Metadata,
    Name,
    Slug,
    Timestamp,
    UuidIdentity,
    Version,
)
from app.infrastructure.database.models.organization_model import (
    OrganizationMemberModel,
    OrganizationModel,
)
from app.infrastructure.repositories.base_repository import BaseRepository


class SQLAlchemyOrganizationRepository(
    BaseRepository[Organization, OrganizationModel, UuidIdentity],
    OrganizationRepository,
):
    """SQLAlchemy implementation of the OrganizationRepository contract.

    Handles persistence for Organization aggregates using AsyncSession and
    OrganizationModel.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository bound to an AsyncSession.

        Args:
            session: The active AsyncSession.
        """
        super().__init__(session, OrganizationModel)

    async def find_by_id(self, id_: UuidIdentity) -> Organization | None:
        """Find an organization by identity.

        Args:
            id_: The identity of the organization to look up.

        Returns:
            The organization aggregate, or None if not found.
        """
        return await self.get_by_id(id_)

    def _to_domain(self, model: OrganizationModel) -> Organization:
        """Convert OrganizationModel into an Organization aggregate root.

        Args:
            model: The OrganizationModel instance.

        Returns:
            The reconstructed Organization domain aggregate root.
        """
        org = Organization(
            organization_id=UuidIdentity(model.id),
            name=Name(model.name),
            slug=Slug(model.slug),
            owner_id=UuidIdentity(model.owner_id),
            status=OrganizationStatus(model.status),
            subscription_plan=SubscriptionPlan(model.subscription_plan),
            created_at=Timestamp(model.created_at),
            updated_at=Timestamp(model.updated_at),
            metadata=Metadata(model.metadata_json),
            version=Version(model.version),
        )

        members_dict = {}
        for m in model.memberships:
            u_id = UuidIdentity(m.user_id)
            members_dict[u_id] = OrganizationMembership(
                user_id=u_id,
                role=UserRole(m.role),
                joined_at=Timestamp(m.joined_at),
                status=MembershipStatus(m.status),
                invitation_accepted=m.invitation_accepted,
            )
        org._members = members_dict
        org.pull_domain_events()
        return org

    def _to_model(
        self, entity: Organization, existing: OrganizationModel | None = None
    ) -> OrganizationModel:
        """Convert an Organization aggregate root into an OrganizationModel instance.

        Args:
            entity: The Organization aggregate root.
            existing: Optional existing OrganizationModel to mutate.

        Returns:
            The populated OrganizationModel.
        """
        if existing is not None:
            existing.name = entity.name.value
            existing.slug = entity.slug.value
            existing.owner_id = entity.owner_id.value
            existing.status = entity.status.value
            existing.subscription_plan = entity.subscription_plan.value
            existing.metadata_json = dict(entity.metadata.value)
            existing.updated_at = entity.updated_at.value
            existing.version = entity.version.major
            target_model = existing
        else:
            target_model = OrganizationModel(
                id=entity.organization_id.value,
                name=entity.name.value,
                slug=entity.slug.value,
                owner_id=entity.owner_id.value,
                status=entity.status.value,
                subscription_plan=entity.subscription_plan.value,
                created_at=entity.created_at.value,
                updated_at=entity.updated_at.value,
                metadata_json=dict(entity.metadata.value),
                version=entity.version.major,
            )

        current_memberships = {m.user_id.value: m for m in entity.members}
        existing_member_models = {m.user_id: m for m in target_model.memberships}

        new_memberships_list = []
        for user_uuid, mem in current_memberships.items():
            if user_uuid in existing_member_models:
                mem_model = existing_member_models[user_uuid]
                mem_model.role = mem.role.value
                mem_model.status = mem.status.value
                mem_model.joined_at = mem.joined_at.value
                mem_model.invitation_accepted = mem.invitation_accepted
                new_memberships_list.append(mem_model)
            else:
                new_memberships_list.append(
                    OrganizationMemberModel(
                        organization_id=entity.organization_id.value,
                        user_id=user_uuid,
                        role=mem.role.value,
                        status=mem.status.value,
                        joined_at=mem.joined_at.value,
                        invitation_accepted=mem.invitation_accepted,
                    )
                )

        target_model.memberships = new_memberships_list
        return target_model

    async def find_by_slug(self, slug: Slug) -> Organization | None:
        """Find an organization by its slug.

        Args:
            slug: The slug to look up.

        Returns:
            The organization, or None if not found.
        """
        stmt = select(OrganizationModel).where(OrganizationModel.slug == slug.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def find_by_owner(self, owner_id: UuidIdentity) -> list[Organization]:
        """Find every organization owned by a user.

        Args:
            owner_id: The identity of the owning user.

        Returns:
            List of organizations owned by the user.
        """
        stmt = select(OrganizationModel).where(
            OrganizationModel.owner_id == owner_id.value
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def exists_by_slug(self, slug: Slug) -> bool:
        """Return whether an organization with the slug exists.

        Args:
            slug: The slug to check.

        Returns:
            True if an organization with the slug exists, False otherwise.
        """
        stmt = select(OrganizationModel.id).where(OrganizationModel.slug == slug.value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

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
            A list of Organization domain aggregates.
        """
        stmt = select(OrganizationModel).offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return [self._to_domain(m) for m in result.scalars().all()]

    async def count(self) -> int:
        """Return the total number of organizations.

        Returns:
            The total organization count.
        """
        from sqlalchemy import func

        stmt = select(func.count()).select_from(OrganizationModel)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())
