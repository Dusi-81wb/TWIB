"""API Keys management v1 endpoints.

Exposes CRUD endpoints for workspace API key management:
- ``POST /api/v1/api-keys``: Create a new API key.
- ``GET /api/v1/api-keys``: List API keys for a workspace.
- ``GET /api/v1/api-keys/{id}``: Get API key details by ID.
- ``DELETE /api/v1/api-keys/{id}``: Revoke an API key.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.tags import API_KEYS
from app.authorization.decorators import RequireWorkspaceRole
from app.authorization.roles import WorkspaceRole
from app.dependencies import get_api_key_service
from app.domain.api_keys.exceptions import InvalidApiKeyError
from app.schemas.api_keys import (
    ApiKeyResponse,
    CreateApiKeyRequest,
    CreatedApiKeyResponse,
)
from app.services.api_keys import ApiKeyService

api_keys_router = APIRouter(prefix="/api-keys", tags=[API_KEYS])


@api_keys_router.post(
    "",
    response_model=CreatedApiKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Workspace API Key",
    description=(
        "Generate a new secure API key for a workspace. "
        "The full plaintext API key is returned ONLY ONCE in the response."
    ),
    dependencies=[Depends(RequireWorkspaceRole(WorkspaceRole.ADMIN))],
    responses={
        201: {
            "description": "API key created successfully.",
        },
        400: {
            "description": "Invalid input payload or workspace ID.",
        },
        403: {
            "description": "Forbidden: Requires Workspace Admin or Owner role.",
        },
    },
)
async def create_api_key(
    payload: CreateApiKeyRequest,
    api_key_service: ApiKeyService = Depends(get_api_key_service),
) -> Any:
    """Create a new workspace-scoped API key.

    Args:
        payload: Request payload containing workspace_id, name, and environment.
        api_key_service: Injected ApiKeyService instance.

    Returns:
        CreatedApiKeyResponse containing key metadata and full plaintext key string.
    """
    try:
        permissions_set = set(payload.permissions) if payload.permissions else None
        key, raw_key_str = await api_key_service.create_api_key(
            workspace_id=payload.workspace_id,
            name=payload.name,
            environment=payload.environment,
            expires_in_days=payload.expires_in_days,
            permissions=permissions_set,
        )
        return CreatedApiKeyResponse(
            id=str(key.id.value),
            workspace_id=str(key.workspace_id.value),
            name=key.name,
            prefix=key.prefix,
            permissions=list(key.permissions),
            created_at=key.created_at.value.isoformat(),
            expires_at=key.expires_at.value.isoformat() if key.expires_at else None,
            last_used_at=key.last_used_at.value.isoformat()
            if key.last_used_at
            else None,
            status=key.status.value,
            api_key=raw_key_str,
        )
    except InvalidApiKeyError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@api_keys_router.get(
    "",
    response_model=list[ApiKeyResponse],
    status_code=status.HTTP_200_OK,
    summary="List Workspace API Keys",
    description="List all active, revoked, and expired API keys for a workspace.",
    dependencies=[Depends(RequireWorkspaceRole(WorkspaceRole.VIEWER))],
    responses={
        200: {
            "description": "List of workspace API keys.",
        },
    },
)
async def list_api_keys(
    workspace_id: str = Query(..., description="Target workspace UUID."),
    api_key_service: ApiKeyService = Depends(get_api_key_service),
) -> Any:
    """List API keys belonging to a workspace.

    Args:
        workspace_id: Target workspace UUID string.
        api_key_service: Injected ApiKeyService instance.

    Returns:
        List of ApiKeyResponse metadata items.
    """
    keys = await api_key_service.list_api_keys_for_workspace(workspace_id)
    return [
        ApiKeyResponse(
            id=str(k.id.value),
            workspace_id=str(k.workspace_id.value),
            name=k.name,
            prefix=k.prefix,
            permissions=list(k.permissions),
            created_at=k.created_at.value.isoformat(),
            expires_at=k.expires_at.value.isoformat() if k.expires_at else None,
            last_used_at=k.last_used_at.value.isoformat() if k.last_used_at else None,
            status=k.status.value,
        )
        for k in keys
    ]


@api_keys_router.get(
    "/{key_id}",
    response_model=ApiKeyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get API Key Details",
    description="Retrieve API key metadata details by API key UUID.",
    responses={
        200: {
            "description": "API key metadata.",
        },
        404: {
            "description": "API key not found.",
        },
    },
)
async def get_api_key(
    key_id: str,
    api_key_service: ApiKeyService = Depends(get_api_key_service),
) -> Any:
    """Get metadata for an API key by ID.

    Args:
        key_id: Target API key UUID string.
        api_key_service: Injected ApiKeyService instance.

    Returns:
        ApiKeyResponse metadata item.

    Raises:
        HTTPException: 404 Not Found if key does not exist.
    """
    key = await api_key_service.get_api_key_by_id(key_id)
    if key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key '{key_id}' not found",
        )

    return ApiKeyResponse(
        id=str(key.id.value),
        workspace_id=str(key.workspace_id.value),
        name=key.name,
        prefix=key.prefix,
        permissions=list(key.permissions),
        created_at=key.created_at.value.isoformat(),
        expires_at=key.expires_at.value.isoformat() if key.expires_at else None,
        last_used_at=key.last_used_at.value.isoformat() if key.last_used_at else None,
        status=key.status.value,
    )


@api_keys_router.delete(
    "/{key_id}",
    response_model=ApiKeyResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke API Key",
    description="Revoke an active API key to prevent future use.",
    responses={
        200: {
            "description": "API key revoked successfully.",
        },
        404: {
            "description": "API key not found.",
        },
    },
)
async def revoke_api_key(
    key_id: str,
    api_key_service: ApiKeyService = Depends(get_api_key_service),
) -> Any:
    """Revoke an API key.

    Args:
        key_id: Target API key UUID string.
        api_key_service: Injected ApiKeyService instance.

    Returns:
        Updated ApiKeyResponse metadata with status='revoked'.

    Raises:
        HTTPException: 404 Not Found if key does not exist.
    """
    try:
        key = await api_key_service.revoke_api_key(key_id)
        return ApiKeyResponse(
            id=str(key.id.value),
            workspace_id=str(key.workspace_id.value),
            name=key.name,
            prefix=key.prefix,
            permissions=list(key.permissions),
            created_at=key.created_at.value.isoformat(),
            expires_at=key.expires_at.value.isoformat() if key.expires_at else None,
            last_used_at=key.last_used_at.value.isoformat()
            if key.last_used_at
            else None,
            status=key.status.value,
        )
    except InvalidApiKeyError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
