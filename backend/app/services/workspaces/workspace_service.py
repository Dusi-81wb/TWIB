"""Workspace application service.

Orchestrates workspace management operations using the Unit of Work,
repositories, and domain aggregate methods. No direct database access;
all persistence goes through the repository layer.
"""

from __future__ import annotations

import uuid

from app.domain.exceptions import BusinessRuleViolation, EntityNotFound
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.value_objects import Description, Name, Slug, UuidIdentity
from app.domain.workspaces.status import WorkspaceStatus
from app.domain.workspaces.workspace import Workspace


class WorkspaceService:
    """Application service managing workspace lifecycle operations.

    All methods interact with the persistence layer exclusively through
    the Unit of Work and its repositories.

    Attributes:
        _uow: Unit of Work for repository access.
    """

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        """Initialize the workspace service.

        Args:
            unit_of_work: Unit of Work for repository access.
        """
        self._uow = unit_of_work

    async def create_workspace(
        self,
        organization_id: str,
        name: str,
        owner_id: str,
        slug: str | None = None,
        description: str | None = None,
    ) -> Workspace:
        """Create a new workspace aggregate and persist it.

        Args:
            organization_id: Parent organization UUID string.
            name: Workspace name string.
            owner_id: UUID string of the owner user.
            slug: Optional custom slug string.
            description: Optional workspace description.

        Returns:
            The created Workspace domain aggregate.

        Raises:
            EntityNotFound: If parent organization does not exist.
            BusinessRuleViolation: If slug is invalid or already taken in org.
        """
        try:
            w_uuid = uuid.uuid4()
            o_uuid = uuid.UUID(organization_id)
            u_uuid = uuid.UUID(owner_id)
            name_vo = Name(name)
            slug_str = slug if slug else name.lower().replace(" ", "-")
            slug_vo = Slug(slug_str)
            desc_vo = Description(description or "")
        except ValueError as err:
            raise BusinessRuleViolation(str(err)) from err

        async with self._uow as uow:
            org = await uow.organizations.find_by_id(UuidIdentity(o_uuid))
            if org is None:
                raise EntityNotFound(f"Organization '{organization_id}' not found")

            if await uow.workspaces.exists_by_slug(UuidIdentity(o_uuid), slug_vo):
                raise BusinessRuleViolation(
                    f"Workspace with slug '{slug_vo.value}' already exists"
                )

            workspace = Workspace(
                workspace_id=UuidIdentity(w_uuid),
                organization_id=UuidIdentity(o_uuid),
                name=name_vo,
                slug=slug_vo,
                description=desc_vo,
                owner_id=UuidIdentity(u_uuid),
                status=WorkspaceStatus.ACTIVE,
            )
            await uow.workspaces.save(workspace)
            await uow.commit()
        return workspace

    async def get_workspace(self, workspace_id: str) -> Workspace:
        """Retrieve a workspace by ID.

        Args:
            workspace_id: UUID string of the target workspace.

        Returns:
            The Workspace domain aggregate.

        Raises:
            EntityNotFound: If workspace does not exist.
        """
        return await self._find_workspace_or_raise(workspace_id)

    async def list_workspaces(
        self,
        limit: int = 50,
        offset: int = 0,
        organization_id: str | None = None,
    ) -> tuple[list[Workspace], int]:
        """List workspaces with pagination and optional organization filter.

        Args:
            limit: Maximum number of workspaces to return.
            offset: Number of workspaces to skip.
            organization_id: Optional organization UUID filter.

        Returns:
            Tuple of (list of Workspace aggregates, total count).
        """
        org_identity: UuidIdentity | None = None
        if organization_id:
            try:
                org_identity = UuidIdentity(uuid.UUID(organization_id))
            except ValueError:
                return [], 0

        async with self._uow as uow:
            workspaces = await uow.workspaces.find_all(
                limit=limit,
                offset=offset,
                organization_id=org_identity,
            )
            total = await uow.workspaces.count(organization_id=org_identity)
        return workspaces, total

    async def update_workspace(
        self,
        workspace_id: str,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> Workspace:
        """Update a workspace's details or status.

        Args:
            workspace_id: UUID string of the target workspace.
            name: Optional new workspace name.
            slug: Optional new URL-friendly slug.
            description: Optional new description.
            status: Optional new status string.

        Returns:
            The updated Workspace domain aggregate.

        Raises:
            EntityNotFound: If workspace does not exist.
            BusinessRuleViolation: If a domain rule is violated.
        """
        async with self._uow as uow:
            try:
                ws_uuid = uuid.UUID(workspace_id)
            except ValueError as err:
                raise EntityNotFound(f"Workspace '{workspace_id}' not found") from err

            ws = await uow.workspaces.find_by_id(UuidIdentity(ws_uuid))
            if ws is None:
                raise EntityNotFound(f"Workspace '{workspace_id}' not found")

            if name is not None:
                ws.rename(Name(name))

            if slug is not None:
                new_slug = Slug(slug)
                if new_slug != ws.slug and await uow.workspaces.exists_by_slug(
                    ws.organization_id, new_slug
                ):
                    raise BusinessRuleViolation(
                        f"Workspace with slug '{new_slug.value}' already exists"
                    )
                ws.change_slug(new_slug)

            if description is not None:
                ws.change_description(Description(description))

            if status is not None:
                self._apply_status_change(ws, status)

            await uow.workspaces.save(ws)
            await uow.commit()
        return ws

    async def delete_workspace(self, workspace_id: str) -> Workspace:
        """Archive a workspace.

        Args:
            workspace_id: UUID string of the target workspace.

        Returns:
            The archived Workspace domain aggregate.

        Raises:
            EntityNotFound: If workspace does not exist.
            BusinessRuleViolation: If a domain rule is violated.
        """
        async with self._uow as uow:
            try:
                ws_uuid = uuid.UUID(workspace_id)
            except ValueError as err:
                raise EntityNotFound(f"Workspace '{workspace_id}' not found") from err

            ws = await uow.workspaces.find_by_id(UuidIdentity(ws_uuid))
            if ws is None:
                raise EntityNotFound(f"Workspace '{workspace_id}' not found")

            ws.archive()
            await uow.workspaces.save(ws)
            await uow.commit()
        return ws

    async def get_members(self, workspace_id: str) -> Workspace:
        """Retrieve a workspace and its members.

        Args:
            workspace_id: Target workspace UUID string.

        Returns:
            The Workspace aggregate with its members.

        Raises:
            EntityNotFound: If workspace does not exist.
        """
        return await self._find_workspace_or_raise(workspace_id)

    async def add_member(
        self,
        workspace_id: str,
        user_id: str,
        role: str = "viewer",
    ) -> Workspace:
        """Add a user as a member to a workspace.

        Args:
            workspace_id: Target workspace UUID string.
            user_id: Target user UUID string.
            role: Workspace role string.

        Returns:
            The updated Workspace aggregate.

        Raises:
            EntityNotFound: If workspace or user does not exist.
            BusinessRuleViolation: If role is invalid or user is already a member.
        """
        from app.domain.workspaces.membership import WorkspaceRole

        try:
            role_enum = WorkspaceRole(role)
            u_uuid = uuid.UUID(user_id)
        except ValueError as err:
            raise BusinessRuleViolation(f"Invalid member configuration: {err}") from err

        async with self._uow as uow:
            ws = await self._find_workspace_or_raise(workspace_id)
            user = await uow.users.find_by_id(UuidIdentity(u_uuid))
            if user is None:
                raise EntityNotFound(f"User '{user_id}' not found")

            ws.add_member(UuidIdentity(u_uuid), role_enum)
            await uow.workspaces.save(ws)
            await uow.commit()
        return ws

    async def update_member_role(
        self,
        workspace_id: str,
        user_id: str,
        role: str,
    ) -> Workspace:
        """Update a workspace member's role.

        Args:
            workspace_id: Target workspace UUID string.
            user_id: Target user UUID string.
            role: New workspace role string.

        Returns:
            The updated Workspace aggregate.

        Raises:
            EntityNotFound: If workspace or member does not exist.
            BusinessRuleViolation: If role is invalid.
        """
        from app.domain.workspaces.membership import WorkspaceRole

        try:
            role_enum = WorkspaceRole(role)
            u_uuid = uuid.UUID(user_id)
        except ValueError as err:
            raise BusinessRuleViolation(f"Invalid role: '{role}'") from err

        async with self._uow as uow:
            ws = await self._find_workspace_or_raise(workspace_id)
            user_identity = UuidIdentity(u_uuid)
            if ws.get_member(user_identity) is None:
                raise EntityNotFound(
                    f"User '{user_id}' is not a member of workspace '{workspace_id}'"
                )

            ws._change_member_role(user_identity, role_enum)
            ws._touch()
            await uow.workspaces.save(ws)
            await uow.commit()
        return ws

    async def remove_member(
        self,
        workspace_id: str,
        user_id: str,
    ) -> Workspace:
        """Remove a member from a workspace.

        Args:
            workspace_id: Target workspace UUID string.
            user_id: Target user UUID string.

        Returns:
            The updated Workspace aggregate.

        Raises:
            EntityNotFound: If workspace or member does not exist.
            BusinessRuleViolation: If owner cannot be removed or state is invalid.
        """
        try:
            u_uuid = uuid.UUID(user_id)
        except ValueError as err:
            raise EntityNotFound(f"User '{user_id}' not found") from err

        async with self._uow as uow:
            ws = await self._find_workspace_or_raise(workspace_id)
            ws.remove_member(UuidIdentity(u_uuid))
            await uow.workspaces.save(ws)
            await uow.commit()
        return ws

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _find_workspace_or_raise(self, workspace_id: str) -> Workspace:
        """Find a workspace by ID or raise EntityNotFound.

        Args:
            workspace_id: UUID string of the target workspace.

        Returns:
            The Workspace domain aggregate.

        Raises:
            EntityNotFound: If workspace does not exist.
        """
        try:
            wid = uuid.UUID(workspace_id)
        except ValueError as err:
            raise EntityNotFound(f"Workspace '{workspace_id}' not found") from err

        async with self._uow as uow:
            ws = await uow.workspaces.find_by_id(UuidIdentity(wid))

        if ws is None:
            raise EntityNotFound(f"Workspace '{workspace_id}' not found")
        return ws

    @staticmethod
    def _apply_status_change(ws: Workspace, status: str) -> None:
        """Apply status transition via domain methods.

        Args:
            ws: Target Workspace aggregate.
            status: Target status string.

        Raises:
            BusinessRuleViolation: If status string is invalid.
        """
        try:
            target = WorkspaceStatus(status)
        except ValueError as err:
            raise BusinessRuleViolation(f"Invalid status: '{status}'") from err

        transitions = {
            WorkspaceStatus.ACTIVE: ws.activate,
            WorkspaceStatus.SUSPENDED: ws.suspend,
            WorkspaceStatus.ARCHIVED: ws.archive,
        }

        handler = transitions.get(target)
        if handler is None:
            raise BusinessRuleViolation(
                f"Cannot transition workspace to status '{status}'"
            )
        handler()
