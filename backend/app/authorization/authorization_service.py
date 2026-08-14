"""Authorization service for evaluating permissions and role access.

Implements reusable methods for checking permissions, organization roles,
workspace roles, and effective permission sets.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable

from app.authorization.policy import (
    get_permissions_for_org_role,
    get_permissions_for_workspace_role,
)
from app.authorization.roles import (
    UserRole,
    WorkspaceRole,
    is_org_role_at_least,
    is_workspace_role_at_least,
)
from app.core.logging import get_logger
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.value_objects import UuidIdentity

logger = get_logger(__name__)


class AuthorizationService:
    """Service evaluating RBAC policy and organization/workspace access rules.

    Attributes:
        _uow: Unit of Work for querying database state.
    """

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        """Initialize the authorization service.

        Args:
            unit_of_work: Unit of Work instance.
        """
        self._uow = unit_of_work

    def has_permission(
        self,
        user_permissions: set[str],
        permission: str,
    ) -> bool:
        """Check if user_permissions includes a target permission.

        Args:
            user_permissions: Set of granted permission strings.
            permission: The permission to check.

        Returns:
            True if granted, False otherwise.
        """
        return permission in user_permissions

    def has_any_permission(
        self,
        user_permissions: set[str],
        permissions: Iterable[str],
    ) -> bool:
        """Check if user_permissions contains at least one of the permissions.

        Args:
            user_permissions: Set of granted permission strings.
            permissions: Iterable of candidate permission strings.

        Returns:
            True if any permission is granted, False otherwise.
        """
        req_set = set(permissions)
        return bool(user_permissions.intersection(req_set))

    def has_all_permissions(
        self,
        user_permissions: set[str],
        permissions: Iterable[str],
    ) -> bool:
        """Check if user_permissions contains all of the specified permissions.

        Args:
            user_permissions: Set of granted permission strings.
            permissions: Iterable of required permission strings.

        Returns:
            True if all required permissions are granted, False otherwise.
        """
        req_set = set(permissions)
        return req_set.issubset(user_permissions)

    async def has_organization_access(
        self,
        user_id: str,
        org_id: str,
        required_role: UserRole | str | None = None,
    ) -> bool:
        """Check if a user has access to an organization with a minimum role.

        Args:
            user_id: User UUID string.
            org_id: Organization UUID string.
            required_role: Minimum required organization role.

        Returns:
            True if access is authorized, False otherwise.
        """
        try:
            u_uuid = uuid.UUID(user_id)
            o_uuid = uuid.UUID(org_id)
        except ValueError:
            return False

        async with self._uow as uow:
            org = await uow.organizations.find_by_id(UuidIdentity(o_uuid))

        if org is None:
            return False

        # Owner has full access
        if str(org.owner_id.value) == str(u_uuid):
            return True

        # Check organization membership
        membership = org.get_member(UuidIdentity(u_uuid))
        if membership is None:
            return False

        if required_role is None:
            return True

        return is_org_role_at_least(membership.role.value, required_role)

    async def has_workspace_access(
        self,
        user_id: str,
        workspace_id: str,
        required_role: WorkspaceRole | str | None = None,
    ) -> bool:
        """Check if a user has access to a workspace with a minimum role.

        Args:
            user_id: User UUID string.
            workspace_id: Workspace UUID string.
            required_role: Minimum required workspace role.

        Returns:
            True if authorized, False otherwise.
        """
        try:
            u_uuid = uuid.UUID(user_id)
            w_uuid = uuid.UUID(workspace_id)
        except ValueError:
            return False

        async with self._uow as uow:
            workspace = await uow.workspaces.find_by_id(UuidIdentity(w_uuid))

        if workspace is None:
            return False

        # Workspace owner or Org owner has full access
        if str(workspace.owner_id.value) == str(u_uuid):
            return True

        membership = workspace.get_member(UuidIdentity(u_uuid))
        if membership is not None:
            if required_role is None:
                return True
            return is_workspace_role_at_least(membership.role.value, required_role)

        # Fallback check on organization owner/admin role
        return await self.has_organization_access(
            user_id=user_id,
            org_id=str(workspace.organization_id.value),
            required_role=UserRole.ADMIN,
        )

    async def get_effective_permissions(
        self,
        user_id: str,
        org_id: str | None = None,
        workspace_id: str | None = None,
    ) -> set[str]:
        """Aggregate all effective permissions for a user within context.

        Args:
            user_id: User UUID string.
            org_id: Optional Organization UUID string.
            workspace_id: Optional Workspace UUID string.

        Returns:
            Set of effective permission strings.
        """
        effective: set[str] = set()

        try:
            u_uuid = uuid.UUID(user_id)
        except ValueError:
            return effective

        async with self._uow as uow:
            user = await uow.users.find_by_id(UuidIdentity(u_uuid))

        if user is None:
            return effective

        # User's default platform role permissions
        effective.update(get_permissions_for_org_role(user.role))

        if org_id:
            try:
                o_uuid = uuid.UUID(org_id)
                async with self._uow as uow:
                    org = await uow.organizations.find_by_id(UuidIdentity(o_uuid))
                if org is not None:
                    if str(org.owner_id.value) == user_id:
                        effective.update(get_permissions_for_org_role(UserRole.OWNER))
                    else:
                        m = org.get_member(UuidIdentity(u_uuid))
                        if m is not None:
                            effective.update(get_permissions_for_org_role(m.role.value))
            except ValueError as e:
                logger.warning("Invalid organization ID format", error=str(e), org_id=org_id)

        if workspace_id:
            try:
                w_uuid = uuid.UUID(workspace_id)
                async with self._uow as uow:
                    ws = await uow.workspaces.find_by_id(UuidIdentity(w_uuid))
                if ws is not None:
                    if str(ws.owner_id.value) == user_id:
                        effective.update(
                            get_permissions_for_workspace_role(WorkspaceRole.OWNER)
                        )
                    else:
                        wm = ws.get_member(UuidIdentity(u_uuid))
                        if wm is not None:
                            effective.update(
                                get_permissions_for_workspace_role(wm.role.value)
                            )
            except ValueError as e:
                logger.warning("Invalid workspace ID format", error=str(e), workspace_id=workspace_id)

        return effective
