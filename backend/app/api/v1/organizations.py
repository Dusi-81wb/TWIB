"""Organization management API router for v1 endpoints.

Exposes endpoints for organization CRUD operations:

- ``POST /api/v1/organizations``: Create a new organization.
- ``GET /api/v1/organizations``: List all organizations (admin).
- ``GET /api/v1/organizations/{organization_id}``: Get organization details.
- ``PATCH /api/v1/organizations/{organization_id}``: Update organization details.
- ``DELETE /api/v1/organizations/{organization_id}``: Archive/delete organization.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.tags import ORGANIZATIONS
from app.authorization.authorization_service import AuthorizationService
from app.authorization.roles import UserRole
from app.dependencies import (
    get_authorization_service,
    get_current_user_claims,
    get_organization_service,
)
from app.domain.exceptions import BusinessRuleViolation, EntityNotFound
from app.schemas.organizations import (
    CreateOrganizationRequest,
    OrganizationListResponse,
    OrganizationMemberResponse,
    OrganizationResponse,
    UpdateOrganizationRequest,
)
from app.services.organizations import OrganizationService

organizations_router = APIRouter(prefix="/organizations", tags=[ORGANIZATIONS])


def _org_to_response(org: Any) -> OrganizationResponse:
    """Convert an Organization domain aggregate into an OrganizationResponse schema.

    Args:
        org: The Organization domain aggregate.

    Returns:
        A serializable OrganizationResponse instance.
    """
    members = [
        OrganizationMemberResponse(
            user_id=str(m.user_id.value),
            role=m.role.value if hasattr(m.role, "value") else str(m.role),
            joined_at=m.joined_at.value.isoformat(),
            status=m.status.value if hasattr(m.status, "value") else str(m.status),
        )
        for m in org.members
    ]

    return OrganizationResponse(
        id=str(org.organization_id.value),
        name=str(org.name.value),
        slug=str(org.slug.value),
        owner_id=str(org.owner_id.value),
        status=org.status.value,
        subscription_plan=org.subscription_plan.value,
        created_at=org.created_at.value.isoformat(),
        updated_at=org.updated_at.value.isoformat(),
        metadata=dict(org.metadata.value),
        members=members,
    )


@organizations_router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Organization",
    description="Create a new organization with the authenticated user as owner.",
)
async def create_organization(
    payload: CreateOrganizationRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    org_service: OrganizationService = Depends(get_organization_service),
) -> Any:
    """Create a new organization.

    Args:
        payload: Organization creation payload.
        claims: Decoded JWT claims with ``sub`` (user_id).
        org_service: Injected OrganizationService dependency.

    Returns:
        Created OrganizationResponse.

    Raises:
        HTTPException: 400 on validation or domain rule violation.
    """
    try:
        org = await org_service.create_organization(
            name=payload.name,
            owner_id=claims["sub"],
            slug=payload.slug,
        )
        return _org_to_response(org)
    except BusinessRuleViolation as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@organizations_router.get(
    "",
    response_model=OrganizationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Organizations",
    description="List all organizations with pagination.",
)
async def list_organizations(
    claims: dict[str, Any] = Depends(get_current_user_claims),
    org_service: OrganizationService = Depends(get_organization_service),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page."),
    offset: int = Query(default=0, ge=0, description="Page offset."),
) -> Any:
    """List organizations with pagination.

    Args:
        claims: Decoded JWT claims.
        org_service: Injected OrganizationService dependency.
        limit: Items per page.
        offset: Skip count.

    Returns:
        OrganizationListResponse.
    """
    orgs, total = await org_service.list_organizations(limit=limit, offset=offset)
    return OrganizationListResponse(
        items=[_org_to_response(o) for o in orgs],
        total=total,
        limit=limit,
        offset=offset,
    )


@organizations_router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Organization by ID",
    description="Retrieve an organization by its UUID identity.",
)
async def get_organization(
    organization_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    org_service: OrganizationService = Depends(get_organization_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
) -> Any:
    """Get an organization by ID.

    Args:
        organization_id: Target organization UUID string.
        claims: Decoded JWT claims.
        org_service: Injected OrganizationService dependency.
        authz_service: Injected AuthorizationService dependency.

    Returns:
        OrganizationResponse.

    Raises:
        HTTPException: 403 if forbidden, 404 if not found.
    """
    has_access = await authz_service.has_organization_access(
        user_id=claims["sub"],
        org_id=organization_id,
    )
    if not has_access and claims.get("role") not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access this organization",
        )

    try:
        org = await org_service.get_organization(organization_id)
        return _org_to_response(org)
    except EntityNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@organizations_router.patch(
    "/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Organization",
    description="Update an organization's details, plan, or status.",
)
async def update_organization(
    organization_id: str,
    payload: UpdateOrganizationRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    org_service: OrganizationService = Depends(get_organization_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
) -> Any:
    """Update an organization by ID.

    Args:
        organization_id: Target organization UUID string.
        payload: Update organization payload.
        claims: Decoded JWT claims.
        org_service: Injected OrganizationService dependency.
        authz_service: Injected AuthorizationService dependency.

    Returns:
        Updated OrganizationResponse.

    Raises:
        HTTPException: 403 if forbidden, 404 if not found, 400 on domain violation.
    """
    has_access = await authz_service.has_organization_access(
        user_id=claims["sub"],
        org_id=organization_id,
        required_role=UserRole.ADMIN,
    )
    if not has_access and claims.get("role") not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update this organization",
        )

    try:
        org = await org_service.update_organization(
            organization_id=organization_id,
            name=payload.name,
            slug=payload.slug,
            subscription_plan=payload.subscription_plan,
            status=payload.status,
        )
        return _org_to_response(org)
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


@organizations_router.delete(
    "/{organization_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete Organization",
    description="Archive an organization by ID.",
)
async def delete_organization(
    organization_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    org_service: OrganizationService = Depends(get_organization_service),
    authz_service: AuthorizationService = Depends(get_authorization_service),
) -> Any:
    """Delete (archive) an organization by ID.

    Args:
        organization_id: Target organization UUID string.
        claims: Decoded JWT claims.
        org_service: Injected OrganizationService dependency.
        authz_service: Injected AuthorizationService dependency.

    Returns:
        Archived OrganizationResponse.

    Raises:
        HTTPException: 403 if forbidden, 404 if not found, 400 on domain violation.
    """
    has_access = await authz_service.has_organization_access(
        user_id=claims["sub"],
        org_id=organization_id,
        required_role=UserRole.OWNER,
    )
    if not has_access and claims.get("role") not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete this organization",
        )

    try:
        org = await org_service.delete_organization(organization_id)
        return _org_to_response(org)
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
