"""Invitation management API router for v1 endpoints.

Exposes endpoints for workspace invitations:

- ``POST /api/v1/invitations``: Create a new workspace invitation.
- ``POST /api/v1/invitations/{id}/accept``: Accept a workspace invitation.
- ``POST /api/v1/invitations/{id}/reject``: Reject a workspace invitation.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.tags import INVITATIONS
from app.authorization.authorization_service import AuthorizationService
from app.authorization.roles import WorkspaceRole
from app.dependencies import (
    get_authorization_service,
    get_current_user_claims,
    get_invitation_service,
)
from app.domain.exceptions import BusinessRuleViolation, EntityNotFound
from app.schemas.invitations import (
    CreateInvitationRequest,
    InvitationResponse,
)
from app.services.invitations import InvitationService

invitations_router = APIRouter(prefix="/invitations", tags=[INVITATIONS])


@invitations_router.post(
    "",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Workspace Invitation",
    description="Issue an invitation for a user to join a workspace.",
)
async def create_invitation(
    payload: CreateInvitationRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    invitation_service: InvitationService = Depends(get_invitation_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
) -> Any:
    """Create a new workspace invitation.

    Args:
        payload: Invitation creation payload.
        claims: Decoded JWT claims with ``sub`` (inviter user_id).
        invitation_service: Injected InvitationService dependency.
        authz_service: Injected AuthorizationService dependency.

    Returns:
        Created InvitationResponse.

    Raises:
        HTTPException: 403 if forbidden, 404 if workspace not found, 400 on error.
    """
    has_access = await authz_service.has_workspace_access(
        user_id=claims["sub"],
        workspace_id=payload.workspace_id,
        required_role=WorkspaceRole.ADMIN,
    )
    if not has_access and claims.get("role") not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to invite members to this workspace",
        )

    try:
        record = await invitation_service.create_invitation(
            workspace_id=payload.workspace_id,
            email=payload.email,
            role=payload.role,
            inviter_id=claims["sub"],
        )
        return InvitationResponse(**record)
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


@invitations_router.post(
    "/{invitation_id}/accept",
    response_model=InvitationResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept Workspace Invitation",
    description="Accept a pending invitation and join the workspace.",
)
async def accept_invitation(
    invitation_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> Any:
    """Accept an invitation.

    Args:
        invitation_id: Target invitation UUID identity.
        claims: Decoded JWT claims with ``sub`` (user_id).
        invitation_service: Injected InvitationService dependency.

    Returns:
        Accepted InvitationResponse.

    Raises:
        HTTPException: 404 if not found, 400 on error.
    """
    try:
        record = await invitation_service.accept_invitation(
            invitation_id=invitation_id,
            user_id=claims["sub"],
        )
        return InvitationResponse(**record)
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


@invitations_router.post(
    "/{invitation_id}/reject",
    response_model=InvitationResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject Workspace Invitation",
    description="Reject a pending workspace invitation.",
)
async def reject_invitation(
    invitation_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    invitation_service: InvitationService = Depends(get_invitation_service),
) -> Any:
    """Reject an invitation.

    Args:
        invitation_id: Target invitation UUID identity.
        claims: Decoded JWT claims with ``sub`` (user_id).
        invitation_service: Injected InvitationService dependency.

    Returns:
        Rejected InvitationResponse.

    Raises:
        HTTPException: 404 if not found, 400 on error.
    """
    try:
        record = await invitation_service.reject_invitation(
            invitation_id=invitation_id,
            user_id=claims["sub"],
        )
        return InvitationResponse(**record)
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
