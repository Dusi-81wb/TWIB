"""User management API router for v1 endpoints.

Exposes endpoints for user CRUD operations:

- ``GET /api/v1/users/me``: Get current authenticated user.
- ``PATCH /api/v1/users/me``: Update current user's profile.
- ``GET /api/v1/users``: List users (admin).
- ``GET /api/v1/users/{user_id}``: Get user by ID (admin).
- ``PATCH /api/v1/users/{user_id}``: Update a user (admin).
- ``DELETE /api/v1/users/{user_id}``: Soft-delete a user (admin).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.tags import USERS
from app.dependencies import get_current_user_claims, get_user_service
from app.domain.exceptions import BusinessRuleViolation, EntityNotFound
from app.schemas.users import (
    UpdateProfileRequest,
    UpdateUserRequest,
    UserListResponse,
    UserResponse,
)
from app.services.users import UserService

users_router = APIRouter(prefix="/users", tags=[USERS])


def _user_to_response(user: Any) -> UserResponse:
    """Convert a User domain aggregate to a UserResponse schema.

    Args:
        user: The User domain aggregate.

    Returns:
        A serializable UserResponse instance.
    """
    return UserResponse(
        id=str(user.user_id.value),
        email=str(user.email.value),
        display_name=str(user.display_name.value),
        role=user.role.value,
        status=user.status.value,
        created_at=user.created_at.value.isoformat(),
        updated_at=user.updated_at.value.isoformat(),
        metadata=dict(user.metadata.value),
    )


@users_router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Retrieve the profile of the currently authenticated user.",
)
async def get_current_user(
    claims: dict[str, Any] = Depends(get_current_user_claims),
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """Return the authenticated user's profile.

    Args:
        claims: Decoded JWT claims with ``sub`` (user_id).
        user_service: Injected UserService dependency.

    Returns:
        UserResponse for the authenticated user.

    Raises:
        HTTPException: 404 if user not found.
    """
    try:
        user = await user_service.get_current_user(claims["sub"])
        return _user_to_response(user)
    except EntityNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@users_router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Current User Profile",
    description=("Update the authenticated user's own display name and/or email."),
)
async def update_current_user_profile(
    payload: UpdateProfileRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """Update the authenticated user's profile.

    Args:
        payload: Profile update payload.
        claims: Decoded JWT claims with ``sub`` (user_id).
        user_service: Injected UserService dependency.

    Returns:
        Updated UserResponse.

    Raises:
        HTTPException: 404 if user not found, 400 on domain violation.
    """
    try:
        user = await user_service.update_profile(
            user_id=claims["sub"],
            display_name=payload.display_name,
            email=payload.email,
        )
        return _user_to_response(user)
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


@users_router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Users",
    description="List all users with pagination. Requires admin role.",
)
async def list_users(
    claims: dict[str, Any] = Depends(get_current_user_claims),
    user_service: UserService = Depends(get_user_service),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page."),
    offset: int = Query(default=0, ge=0, description="Page offset."),
) -> Any:
    """List users with pagination.

    Only admin or owner roles may list users.

    Args:
        claims: Decoded JWT claims.
        user_service: Injected UserService dependency.
        limit: Maximum number of users per page.
        offset: Number of users to skip.

    Returns:
        UserListResponse with paginated user items.

    Raises:
        HTTPException: 403 if caller is not admin or owner.
    """
    caller_role = claims.get("role", "")
    if caller_role not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to list users",
        )

    users, total = await user_service.list_users(limit=limit, offset=offset)
    return UserListResponse(
        items=[_user_to_response(u) for u in users],
        total=total,
        limit=limit,
        offset=offset,
    )


@users_router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User by ID",
    description="Retrieve a user by UUID. Requires admin role.",
)
async def get_user(
    user_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """Return a specific user by ID.

    Args:
        user_id: Target user UUID string.
        claims: Decoded JWT claims.
        user_service: Injected UserService dependency.

    Returns:
        UserResponse for the requested user.

    Raises:
        HTTPException: 403 if not admin/owner, 404 if not found.
    """
    caller_role = claims.get("role", "")
    if caller_role not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view user details",
        )

    try:
        user = await user_service.get_user(user_id)
        return _user_to_response(user)
    except EntityNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@users_router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update User",
    description=("Admin-level update of a user's profile, role, or status."),
)
async def update_user(
    user_id: str,
    payload: UpdateUserRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """Update a user by ID (admin operation).

    Args:
        user_id: Target user UUID string.
        payload: Admin update payload.
        claims: Decoded JWT claims.
        user_service: Injected UserService dependency.

    Returns:
        Updated UserResponse.

    Raises:
        HTTPException: 403 if not admin/owner, 404 if not found,
            400 on domain violation.
    """
    caller_role = claims.get("role", "")
    if caller_role not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to update users",
        )

    try:
        user = await user_service.update_user(
            user_id=user_id,
            display_name=payload.display_name,
            email=payload.email,
            role=payload.role,
            status=payload.status,
        )
        return _user_to_response(user)
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


@users_router.delete(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete User",
    description="Soft-delete a user. Requires admin role.",
)
async def delete_user(
    user_id: str,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    user_service: UserService = Depends(get_user_service),
) -> Any:
    """Soft-delete a user by ID (admin operation).

    Args:
        user_id: Target user UUID string.
        claims: Decoded JWT claims.
        user_service: Injected UserService dependency.

    Returns:
        The deleted UserResponse.

    Raises:
        HTTPException: 403 if not admin/owner, 404 if not found,
            400 on domain violation.
    """
    caller_role = claims.get("role", "")
    if caller_role not in ("admin", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete users",
        )

    try:
        user = await user_service.delete_user(user_id)
        return _user_to_response(user)
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
