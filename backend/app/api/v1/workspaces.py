"""Workspace management API router for v1 endpoints.

Exposes endpoints for workspace CRUD operations:

- ``POST /api/v1/workspaces``: Create a new workspace.
- ``GET /api/v1/workspaces``: List workspaces (with optional organization filter).
- ``GET /api/v1/workspaces/{workspace_id}``: Get workspace details.
- ``PATCH /api/v1/workspaces/{workspace_id}``: Update workspace details.
- ``DELETE /api/v1/workspaces/{workspace_id}``: Archive/delete workspace.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.tags import WORKSPACES
from app.authorization.authorization_service import AuthorizationService
from app.authorization.roles import WorkspaceRole
from app.dependencies import (
    get_authorization_service,
    get_current_user_claims,
    get_workspace_service,
)
from app.domain.exceptions import BusinessRuleViolation, EntityNotFound
from app.schemas.invitations import UpdateMemberRoleRequest
from app.schemas.workspaces import (
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
    WorkspaceListResponse,
    WorkspaceMemberResponse,
    WorkspaceResponse,
)
from app.services.workspaces import WorkspaceService

workspaces_router = APIRouter(prefix="/workspaces", tags=[WORKSPACES])


def _workspace_to_response(ws: Any) -> WorkspaceResponse:
    """Convert a Workspace domain aggregate into a WorkspaceResponse schema.

    Args:
        ws: The Workspace domain aggregate.

    Returns:
        A serializable WorkspaceResponse instance.
    """
    members = [
        WorkspaceMemberResponse(
            user_id=str(m.user_id.value),
            role=m.role.value if hasattr(m.role, "value") else str(m.role),
            joined_at=m.joined_at.value.isoformat(),
            status=m.status.value if hasattr(m.status, "value") else str(m.status),
        )
        for m in ws.members
    ]

    return WorkspaceResponse(
        id=str(ws.workspace_id.value),
        organization_id=str(ws.organization_id.value),
        name=str(ws.name.value),
        slug=str(ws.slug.value),
        description=str(ws.description.value) if ws.description else "",
        owner_id=str(ws.owner_id.value),
        status=ws.status.value,
        created_at=ws.created_at.value.isoformat(),
        updated_at=ws.updated_at.value.isoformat(),
        metadata=dict(ws.metadata.value),
        members=members,
    )


@workspaces_router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Workspace",
    description="Create a new workspace inside an organization.",
)
async def create_workspace(
    payload: CreateWorkspaceRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
) -> Any:
    """Create a new workspace.

    Args:
        payload: Workspace creation payload.
        claims: Decoded JWT claims with ``sub`` (user_id).
        workspace_service: Injected WorkspaceService dependency.
        authz_service: Injected AuthorizationService dependency.

    Returns:
        Created WorkspaceResponse.

    Raises:
        HTTPException: 403 if forbidden, 404 if org not found, 400 on domain error.
    """
    has_access = await authz_service.has_organization_access(
        user_id=claims["sub"],
        org_id=payload.organization_id,
    )
    if not has_access and claims.get("role") not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create workspace in organization",
        )

    try:
        ws = await workspace_service.create_workspace(
            organization_id=payload.organization_id,
            name=payload.name,
            owner_id=claims["sub"],
            slug=payload.slug,
            description=payload.description,
        )
        return _workspace_to_response(ws)
    except EntityNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except BusinessRuleViolation as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@workspaces_router.get(
    "",
    response_model=WorkspaceListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Workspaces",
    description="List all workspaces with optional organization filter and pagination.",
)
async def list_workspaces(
    claims: dict[str, Any] = Depends(get_current_user_claims),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    organization_id: str | None = Query(
        default=None, description="Optional organization UUID filter."
    ),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page."),
    offset: int = Query(default=0, ge=0, description="Page offset."),
) -> Any:
    """List workspaces with pagination.

    Args:
        claims: Decoded JWT claims.
        workspace_service: Injected WorkspaceService dependency.
        organization_id: Optional org UUID filter.
        limit: Items per page.
        offset: Skip count.

    Returns:
        WorkspaceListResponse.
    """
    workspaces, total = await workspace_service.list_workspaces(
        limit=limit,
        offset=offset,
        organization_id=organization_id,
    )
    return WorkspaceListResponse(
        items=[_workspace_to_response(w) for w in workspaces],
        total=total,
        limit=limit,
        offset=offset,
    )


@workspaces_router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Workspace by ID",
    description="Retrieve a workspace by its UUID identity.",
)
async def get_workspace(
    workspace_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
) -> Any:
    """Get a workspace by ID.

    Args:
        workspace_id: Target workspace UUID string.
        claims: Decoded JWT claims.
        workspace_service: Injected WorkspaceService dependency.
        authz_service: Injected AuthorizationService dependency.

    Returns:
        WorkspaceResponse.

    Raises:
        HTTPException: 403 if forbidden, 404 if not found.
    """
    has_access = await authz_service.has_workspace_access(
        user_id=claims["sub"],
        workspace_id=workspace_id,
    )
    if not has_access and claims.get("role") not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access this workspace",
        )

    try:
        ws = await workspace_service.get_workspace(workspace_id)
        return _workspace_to_response(ws)
    except EntityNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@workspaces_router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Workspace",
    description="Update a workspace's details or status.",
)
async def update_workspace(
    workspace_id: str,
    payload: UpdateWorkspaceRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
) -> Any:
    """Update a workspace by ID.

    Args:
        workspace_id: Target workspace UUID string.
        payload: Update workspace payload.
        claims: Decoded JWT claims.
        workspace_service: Injected WorkspaceService dependency.
        authz_service: Injected AuthorizationService dependency.

    Returns:
        Updated WorkspaceResponse.

    Raises:
        HTTPException: 403 if forbidden, 404 if not found, 400 on domain error.
    """
    has_access = await authz_service.has_workspace_access(
        user_id=claims["sub"],
        workspace_id=workspace_id,
        required_role=WorkspaceRole.ADMIN,
    )
    if not has_access and claims.get("role") not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update this workspace",
        )

    try:
        ws = await workspace_service.update_workspace(
            workspace_id=workspace_id,
            name=payload.name,
            slug=payload.slug,
            description=payload.description,
            status=payload.status,
        )
        return _workspace_to_response(ws)
    except EntityNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except BusinessRuleViolation as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@workspaces_router.delete(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete Workspace",
    description="Archive a workspace by ID.",
)
async def delete_workspace(
    workspace_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
) -> Any:
    """Delete (archive) a workspace by ID.

    Args:
        workspace_id: Target workspace UUID string.
        claims: Decoded JWT claims.
        workspace_service: Injected WorkspaceService dependency.
        authz_service: Injected AuthorizationService dependency.

    Returns:
        Archived WorkspaceResponse.

    Raises:
        HTTPException: 403 if forbidden, 404 if not found, 400 on domain error.
    """
    has_access = await authz_service.has_workspace_access(
        user_id=claims["sub"],
        workspace_id=workspace_id,
        required_role=WorkspaceRole.OWNER,
    )
    if not has_access and claims.get("role") not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete this workspace",
        )

    try:
        ws = await workspace_service.delete_workspace(workspace_id)
        return _workspace_to_response(ws)
    except EntityNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except BusinessRuleViolation as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@workspaces_router.get(
    "/{workspace_id}/members",
    response_model=list[WorkspaceMemberResponse],
    status_code=status.HTTP_200_OK,
    summary="List Workspace Members",
    description="Retrieve all members belonging to a workspace.",
)
async def list_workspace_members(
    workspace_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
) -> Any:
    """List members of a workspace.

    Args:
        workspace_id: Target workspace UUID string.
        claims: Decoded JWT claims.
        workspace_service: Injected WorkspaceService dependency.
        authz_service: Injected AuthorizationService dependency.

    Returns:
        List of WorkspaceMemberResponse objects.

    Raises:
        HTTPException: 403 if forbidden, 404 if workspace not found.
    """
    has_access = await authz_service.has_workspace_access(
        user_id=claims["sub"],
        workspace_id=workspace_id,
    )
    if not has_access and claims.get("role") not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view workspace members",
        )

    try:
        ws = await workspace_service.get_members(workspace_id)
        return _workspace_to_response(ws).members
    except EntityNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@workspaces_router.patch(
    "/{workspace_id}/members/{user_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Workspace Member Role",
    description="Update a member's role within a workspace.",
)
async def update_workspace_member(
    workspace_id: str,
    user_id: str,
    payload: UpdateMemberRoleRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
) -> Any:
    """Update a member's role inside a workspace.

    Args:
        workspace_id: Target workspace UUID string.
        user_id: Member user UUID string.
        payload: UpdateMemberRoleRequest containing new role.
        claims: Decoded JWT claims.
        workspace_service: Injected WorkspaceService dependency.
        authz_service: Injected AuthorizationService dependency.

    Returns:
        Updated WorkspaceResponse.

    Raises:
        HTTPException: 403 if forbidden, 404 if not found, 400 on domain error.
    """
    has_access = await authz_service.has_workspace_access(
        user_id=claims["sub"],
        workspace_id=workspace_id,
        required_role=WorkspaceRole.ADMIN,
    )
    if not has_access and claims.get("role") not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update workspace member role",
        )

    try:
        ws = await workspace_service.update_member_role(
            workspace_id=workspace_id,
            user_id=user_id,
            role=payload.role,
        )
        return _workspace_to_response(ws)
    except EntityNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except BusinessRuleViolation as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@workspaces_router.delete(
    "/{workspace_id}/members/{user_id}",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove Workspace Member",
    description="Remove a member from a workspace.",
)
async def remove_workspace_member(
    workspace_id: str,
    user_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    workspace_service: WorkspaceService = Depends(get_workspace_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
) -> Any:
    """Remove a member from a workspace.

    Args:
        workspace_id: Target workspace UUID string.
        user_id: Member user UUID string.
        claims: Decoded JWT claims.
        workspace_service: Injected WorkspaceService dependency.
        authz_service: Injected AuthorizationService dependency.

    Returns:
        Updated WorkspaceResponse.

    Raises:
        HTTPException: 403 if forbidden, 404 if not found, 400 on domain error.
    """
    has_access = await authz_service.has_workspace_access(
        user_id=claims["sub"],
        workspace_id=workspace_id,
        required_role=WorkspaceRole.ADMIN,
    )
    if not has_access and claims.get("role") not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to remove workspace member",
        )

    try:
        ws = await workspace_service.remove_member(
            workspace_id=workspace_id,
            user_id=user_id,
        )
        return _workspace_to_response(ws)
    except EntityNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except BusinessRuleViolation as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
