"""API Key authentication dependency guard.

Extracts and validates API keys from request headers.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from app.dependencies import get_api_key_service
from app.domain.api_keys import (
    ApiKey,
    ApiKeyExpiredError,
    ApiKeyRevokedError,
    InvalidApiKeyError,
)
from app.services.api_keys import ApiKeyService


async def get_api_key_identity(
    request: Request,
    api_key_service: ApiKeyService = Depends(get_api_key_service),
) -> ApiKey:
    """Extract and verify API key identity from request headers.

    Checks:
    1. ``X-API-Key`` header
    2. ``Authorization: Bearer <twib_...>`` header

    Args:
        request: Active FastAPI request.
        api_key_service: Injected ApiKeyService instance.

    Returns:
        Verified ApiKey aggregate entity.

    Raises:
        HTTPException: 401 Unauthorized if missing, invalid, expired, or revoked.
    """
    raw_key: str | None = request.headers.get("x-api-key")

    if not raw_key:
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token_part = auth_header.split(" ", 1)[1].strip()
            if token_part.startswith("twib_"):
                raw_key = token_part

    if not raw_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide via X-API-Key or Bearer header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return await api_key_service.verify_api_key(raw_key)
    except (InvalidApiKeyError, ApiKeyExpiredError, ApiKeyRevokedError) as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
