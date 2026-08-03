"""SQLAlchemy Workspace repository implementation.

This module implements
:class:`~app.domain.repositories.workspace_repository.WorkspaceRepository`
backed by SQLAlchemy 2.0 and
:class:`app.infrastructure.database.models.workspace_model.WorkspaceModel`.
It translates between the domain aggregate
:class:`app.domain.workspaces.workspace.Workspace`
and the persistence layer.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.workspace_repository import WorkspaceRepository
from app.domain.value_objects import (
    Description,
    Metadata,
    Name,
    Slug,
    Timestamp,
    UuidIdentity,
    Version,
)
from app.domain.workspaces.membership import (
    WorkspaceMembership,
    WorkspaceMembershipStatus,
    WorkspaceRole,
)
from app.domain.workspaces.settings import WorkspaceSettings, WorkspaceVisibility
from app.domain.workspaces.status import WorkspaceStatus
from app.domain.workspaces.workspace import Workspace
from app.infrastructure.database.models.workspace_model import (
    WorkspaceMemberModel,
    WorkspaceModel,
)
from app.infrastructure.repositories.base_repository import BaseRepository


class SQLAlchemyWorkspaceRepository(
    BaseRepository[Workspace, WorkspaceModel, UuidIdentity], WorkspaceRepository
):
    """SQLAlchemy implementation of the WorkspaceRepository contract.

    Handles persistence for Workspace aggregates using AsyncSession and
    WorkspaceModel.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository bound to an AsyncSession.

        Args:
            session: The active AsyncSession.
        """
        super().__init__(session, WorkspaceModel)

    async def find_by_id(self, id_: UuidIdentity) -> Workspace | None:
        """Find a workspace by identity.

        Args:
            id_: The identity of the workspace to look up.

        Returns:
            The workspace aggregate, or None if not found.
        """
        return await self.get_by_id(id_)

    def _to_domain(self, model: WorkspaceModel) -> Workspace:
        """Convert a WorkspaceModel ORM instance into a Workspace domain aggregate root.

        Args:
            model: The WorkspaceModel instance.

        Returns:
            The reconstructed Workspace domain aggregate root.
        """
        s_data = model.settings_json or {}
        ws = Workspace(
            workspace_id=UuidIdentity(model.id),
            organization_id=UuidIdentity(model.organization_id),
            name=Name(model.name),
            slug=Slug(model.slug),
            description=Description(model.description or ""),
            owner_id=UuidIdentity(model.owner_id),
            status=WorkspaceStatus(model.status),
            settings=WorkspaceSettings(
                timezone=s_data.get("timezone", "UTC"),
                default_language=s_data.get("default_language", "en"),
                visibility=WorkspaceVisibility(s_data.get("visibility", "private")),
                ai_model_preference=s_data.get("ai_model_preference", "auto"),
                execution_limits=s_data.get("execution_limits", 5),
                knowledge_base_enabled=s_data.get("knowledge_base_enabled", False),
                experimental_features=s_data.get("experimental_features", False),
            ),
            created_at=Timestamp(model.created_at),
            updated_at=Timestamp(model.updated_at),
            metadata=Metadata(model.metadata_json),
            version=Version(model.version),
        )

        members_dict = {}
        for m in model.memberships:
            u_id = UuidIdentity(m.user_id)
            members_dict[u_id] = WorkspaceMembership(
                user_id=u_id,
                role=WorkspaceRole(m.role),
                joined_at=Timestamp(m.joined_at),
                status=WorkspaceMembershipStatus(m.status),
                invitation_accepted=m.invitation_accepted,
            )
        ws._members = members_dict
        ws.pull_domain_events()
        return ws

    def _to_model(
        self, entity: Workspace, existing: WorkspaceModel | None = None
    ) -> WorkspaceModel:
        """Convert a Workspace aggregate root into a WorkspaceModel instance.

        Args:
            entity: The Workspace aggregate root.
            existing: Optional existing WorkspaceModel to mutate.

        Returns:
            The populated WorkspaceModel.
        """
        settings_dict = {
            "timezone": entity.settings.timezone,
            "default_language": entity.settings.default_language,
            "visibility": entity.settings.visibility.value,
            "ai_model_preference": entity.settings.ai_model_preference,
            "execution_limits": entity.settings.execution_limits,
            "knowledge_base_enabled": entity.settings.knowledge_base_enabled,
            "experimental_features": entity.settings.experimental_features,
        }

        if existing is not None:
            existing.organization_id = entity.organization_id.value
            existing.owner_id = entity.owner_id.value
            existing.name = entity.name.value
            existing.slug = entity.slug.value
            existing.description = entity.description.value
            existing.status = entity.status.value
            existing.settings_json = settings_dict
            existing.metadata_json = dict(entity.metadata.value)
            existing.updated_at = entity.updated_at.value
            existing.version = entity.version.major
            target_model = existing
        else:
            target_model = WorkspaceModel(
                id=entity.workspace_id.value,
                organization_id=entity.organization_id.value,
                owner_id=entity.owner_id.value,
                name=entity.name.value,
                slug=entity.slug.value,
                description=entity.description.value,
                status=entity.status.value,
                settings_json=settings_dict,
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
                    WorkspaceMemberModel(
                        workspace_id=entity.workspace_id.value,
                        user_id=user_uuid,
                        role=mem.role.value,
                        status=mem.status.value,
                        joined_at=mem.joined_at.value,
                        invitation_accepted=mem.invitation_accepted,
                    )
                )

        target_model.memberships = new_memberships_list
        return target_model

    async def find_by_slug(
        self, organization_id: UuidIdentity, slug: Slug
    ) -> Workspace | None:
        """Find a workspace by slug inside an organization.

        Args:
            organization_id: Parent organization identity.
            slug: Workspace slug to look up.

        Returns:
            The workspace aggregate, or None if not found.
        """
        stmt = select(WorkspaceModel).where(
            WorkspaceModel.organization_id == organization_id.value,
            WorkspaceModel.slug == slug.value,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def find_by_organization(
        self, organization_id: UuidIdentity
    ) -> list[Workspace]:
        """Find every workspace in an organization.

        Args:
            organization_id: Parent organization identity.

        Returns:
            List of workspaces in the organization.
        """
        stmt = select(WorkspaceModel).where(
            WorkspaceModel.organization_id == organization_id.value
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def find_by_owner(self, owner_id: UuidIdentity) -> list[Workspace]:
        """Find every workspace owned by a user.

        Args:
            owner_id: Identity of the owning user.

        Returns:
            List of workspaces owned by the user.
        """
        stmt = select(WorkspaceModel).where(WorkspaceModel.owner_id == owner_id.value)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def exists_by_slug(self, organization_id: UuidIdentity, slug: Slug) -> bool:
        """Check whether a workspace with the slug exists in an organization.

        Args:
            organization_id: Parent organization identity.
            slug: Workspace slug to check.

        Returns:
            True if present, False otherwise.
        """
        stmt = select(WorkspaceModel.id).where(
            WorkspaceModel.organization_id == organization_id.value,
            WorkspaceModel.slug == slug.value,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
