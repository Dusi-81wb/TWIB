"""Authentication API router for v1 endpoints.

Exposes endpoints for user authentication and session management:
- ``POST /api/v1/auth/login``: Authenticate credentials, issue access & refresh tokens.
- ``POST /api/v1/auth/refresh``: Rotate refresh token and issue a new access token.
- ``POST /api/v1/auth/logout``: Terminate current session in Redis.
- ``POST /api/v1/auth/logout-all``: Invalidate all active sessions for a user.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.tags import AUTHENTICATION
from app.dependencies import get_authentication_service, get_session_service
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
)
from app.security.exceptions import AuthenticationError, InvalidTokenError
from app.security.refresh_token import hash_refresh_token
from app.security.session import SessionData
from app.services.auth import AuthenticationService, SessionService

auth_router = APIRouter(prefix="/auth", tags=[AUTHENTICATION])


@auth_router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description=(
        "Authenticate a user using their registered email address and password. "
        "Creates a new session in Redis and returns access and refresh tokens."
    ),
    responses={
        200: {
            "description": "Successful authentication with tokens.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "dGhpcy1pcy1hLXJlZnJlc2gtdG9rZW4...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "user": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "user@example.com",
                            "display_name": "Jane Doe",
                            "role": "member",
                            "status": "active",
                        },
                    }
                }
            },
        },
        401: {
            "description": "Invalid email or password.",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid email or password"}
                }
            },
        },
        422: {
            "description": "Validation error in request payload.",
        },
    },
)
async def login(
    request: Request,
    payload: LoginRequest,
    auth_service: AuthenticationService = Depends(get_authentication_service),
) -> Any:
    """Authenticate credentials, create a session, and issue tokens.

    Args:
        request: Active FastAPI HTTP request.
        payload: Credentials payload containing email and password.
        auth_service: Injected AuthenticationService dependency.

    Returns:
        LoginResponse containing access token, refresh token, and user summary.

    Raises:
        HTTPException: 401 Unauthorized if authentication fails.
    """
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host if request.client else ""

    try:
        result = await auth_service.authenticate_user(
            email=payload.email,
            password=payload.password,
            user_agent=user_agent,
            ip_address=client_ip,
        )
        return result
    except AuthenticationError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


@auth_router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description=(
        "Rotate an active refresh token and issue a new JWT access token. "
        "Invalidates the old refresh token upon success."
    ),
    responses={
        200: {
            "description": "Token refreshed and rotated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "bmV3LXJlZnJlc2gtdG9rZW4tc3RyaW5n...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                    }
                }
            },
        },
        401: {
            "description": "Invalid or expired refresh token.",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or expired refresh token"}
                }
            },
        },
    },
)
async def refresh(
    payload: RefreshRequest,
    session_service: SessionService = Depends(get_session_service),
) -> Any:
    """Refresh access token using a valid refresh token.

    Args:
        payload: Refresh payload containing the active refresh_token string.
        session_service: Injected SessionService dependency.

    Returns:
        RefreshResponse containing new access_token and rotated refresh_token.

    Raises:
        HTTPException: 401 Unauthorized if refresh token is invalid or expired.
    """
    try:
        result = await session_service.refresh_tokens(payload.refresh_token)
        return result
    except InvalidTokenError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


@auth_router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Invalidate current session in Redis and acknowledge logout.",
    responses={
        200: {
            "description": "Successfully logged out.",
            "content": {
                "application/json": {
                    "example": {"message": "Successfully logged out"}
                }
            },
        }
    },
)
async def logout(
    payload: RefreshRequest | None = None,
    auth_service: AuthenticationService = Depends(get_authentication_service),
    session_service: SessionService = Depends(get_session_service),
) -> Any:
    """Perform session logout and invalidation.

    Args:
        payload: Optional RefreshRequest payload containing refresh_token.
        auth_service: Injected AuthenticationService dependency.
        session_service: Injected SessionService dependency.

    Returns:
        LogoutResponse containing success message.
    """
    refresh_token = payload.refresh_token if payload else None
    if refresh_token:
        await session_service.invalidate_session_by_token(refresh_token)
    await auth_service.logout_user(refresh_token=refresh_token)
    return LogoutResponse(message="Successfully logged out")


@auth_router.post(
    "/logout-all",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout All Devices",
    description="Invalidate every active session belonging to a specified user.",
    responses={
        200: {
            "description": "Successfully logged out from all devices.",
            "content": {
                "application/json": {
                    "example": {"message": "Successfully logged out from all devices"}
                }
            },
        }
    },
)
async def logout_all(
    user_id: str | None = None,
    payload: RefreshRequest | None = None,
    session_service: SessionService = Depends(get_session_service),
) -> Any:
    """Invalidate all active sessions for a user across all devices.

    Args:
        user_id: Optional explicit user UUID string.
        payload: Optional RefreshRequest containing refresh_token to resolve user.
        session_service: Injected SessionService dependency.

    Returns:
        LogoutResponse containing success message.
    """
    target_user_id = user_id
    if not target_user_id and payload and payload.refresh_token:
        try:
            old_hash = hash_refresh_token(payload.refresh_token)
            session_id = await session_service._redis.get(f"refresh_hash:{old_hash}")
            if session_id:
                session_json = await session_service._redis.get(
                    f"session:{session_id}"
                )
                if session_json:
                    session_data = SessionData.from_json(session_json)
                    target_user_id = session_data.user_id
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or session provided",
            ) from err

    if target_user_id:
        await session_service.invalidate_all_user_sessions(target_user_id)

    return LogoutResponse(message="Successfully logged out from all devices")
