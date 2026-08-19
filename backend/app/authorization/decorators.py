"""FastAPI authorization dependency callables and guards.

Provides reusable dependency classes for enforcing permissions, organization
roles, and workspace roles on endpoints:
- ``RequirePermission(permission)``
- ``RequireOrganizationRole(required_role)``
- ``RequireWorkspaceRole(required_role)``
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, Request, status

from app.authorization.authorization_service import AuthorizationService
from app.authorization.roles import UserRole, WorkspaceRole


def _deps_get_current_user_claims(request: Request) -> dict[str, Any]:
    """Lazy wrapper for get_current_user_claims to avoid circular imports."""
    from app.dependencies import get_current_user_claims

    return get_current_user_claims(request)


def _deps_get_authorization_service(request: Request) -> AuthorizationService:
    """Lazy wrapper for get_authorization_service to avoid circular imports."""
    from app.dependencies import get_authorization_service

    return get_authorization_service(request)


class RequirePermission:
    """FastAPI dependency enforcing that the user holds a specific permission."""

    def __init__(self, permission: str) -> None:
        """Initialize permission requirement.

        Args:
            permission: Target permission string to enforce.
        """
        self.permission = permission

    async def __call__(
        self,
        request: Request,
        claims: dict[str, Any] = Depends(_deps_get_current_user_claims),
        authz_service: AuthorizationService = Depends(_deps_get_authorization_service),
    ) -> dict[str, Any]:
        """Evaluate permission requirement against active request and user.

        Args:
            request: Active FastAPI request.
            claims: Authenticated user token claims.
            authz_service: AuthorizationService instance.

        Returns:
            The user token claims dictionary.

        Raises:
            HTTPException: 403 Forbidden if user lacks required permission.
        """
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication claims",
            )

        path_params = request.path_params
        query_params = request.query_params

        org_id = path_params.get("org_id") or query_params.get("org_id")
        workspace_id = path_params.get("workspace_id") or query_params.get(
            "workspace_id"
        )

        permissions = await authz_service.get_effective_permissions(
            user_id=user_id,
            org_id=org_id,
            workspace_id=workspace_id,
        )

        if not authz_service.has_permission(permissions, self.permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Permission '{self.permission}' required",
            )

        return claims


class RequireOrganizationRole:
    """FastAPI dependency enforcing minimum organization role requirement."""

    def __init__(self, required_role: UserRole | str) -> None:
        """Initialize organization role requirement.

        Args:
            required_role: Minimum required organization role.
        """
        self.required_role = required_role

    async def __call__(
        self,
        request: Request,
        claims: dict[str, Any] = Depends(_deps_get_current_user_claims),
        authz_service: AuthorizationService = Depends(_deps_get_authorization_service),
    ) -> dict[str, Any]:
        """Evaluate organization role requirement.

        Args:
            request: Active FastAPI request.
            claims: Authenticated user token claims.
            authz_service: AuthorizationService instance.

        Returns:
            The user token claims dictionary.

        Raises:
            HTTPException: 403 Forbidden or 400 Bad Request.
        """
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication claims",
            )

        org_id = request.path_params.get("org_id") or request.query_params.get("org_id")
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization ID parameter 'org_id' is required for role check",
            )

        has_access = await authz_service.has_organization_access(
            user_id=user_id,
            org_id=org_id,
            required_role=self.required_role,
        )

        if not has_access:
            role_name = (
                self.required_role.value
                if isinstance(self.required_role, UserRole)
                else str(self.required_role)
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Minimum organization role '{role_name}' required",
            )

        return claims


class RequireWorkspaceRole:
    """FastAPI dependency enforcing minimum workspace role requirement."""

    def __init__(self, required_role: WorkspaceRole | str) -> None:
        """Initialize workspace role requirement.

        Args:
            required_role: Minimum required workspace role.
        """
        self.required_role = required_role

    async def __call__(
        self,
        request: Request,
        claims: dict[str, Any] = Depends(_deps_get_current_user_claims),
        authz_service: AuthorizationService = Depends(_deps_get_authorization_service),
    ) -> dict[str, Any]:
        """Evaluate workspace role requirement.

        Args:
            request: Active FastAPI request.
            claims: Authenticated user token claims.
            authz_service: AuthorizationService instance.

        Returns:
            The user token claims dictionary.

        Raises:
            HTTPException: 403 Forbidden or 400 Bad Request.
        """
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication claims",
            )

        path_params = request.path_params
        query_params = request.query_params

        workspace_id = path_params.get("workspace_id") or query_params.get(
            "workspace_id"
        )
        if not workspace_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Workspace ID parameter 'workspace_id' is required for role check"
                ),
            )

        has_access = await authz_service.has_workspace_access(
            user_id=user_id,
            workspace_id=workspace_id,
            required_role=self.required_role,
        )

        if not has_access:
            role_name = (
                self.required_role.value
                if isinstance(self.required_role, WorkspaceRole)
                else str(self.required_role)
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Minimum workspace role '{role_name}' required",
            )

        return claims


def require_permission(permission: str) -> Callable[..., Any]:
    """Helper creating a RequirePermission dependency callable."""
    return RequirePermission(permission)


def require_organization_role(required_role: UserRole | str) -> Callable[..., Any]:
    """Helper creating a RequireOrganizationRole dependency callable."""
    return RequireOrganizationRole(required_role)


def require_workspace_role(required_role: WorkspaceRole | str) -> Callable[..., Any]:
    """Helper creating a RequireWorkspaceRole dependency callable."""
    return RequireWorkspaceRole(required_role)
