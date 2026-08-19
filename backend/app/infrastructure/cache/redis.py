"""Redis infrastructure entry point.

This module provides lifecycle helpers and high-level factory functions for
accessing the Redis cache infrastructure.
"""

from __future__ import annotations

from app.core.settings import ApplicationSettings
from app.infrastructure.cache.client import RedisClient
from app.infrastructure.cache.connection import (
    check_redis_health,
    close_redis_connection,
    get_redis_connection,
    get_redis_pool,
)

_client: RedisClient | None = None


def get_redis_client(settings: ApplicationSettings | None = None) -> RedisClient:
    """Return the shared RedisClient instance.

    Args:
        settings: Optional application settings.

    Returns:
        The cached RedisClient instance.
    """
    global _client
    if _client is None:
        _client = RedisClient(redis_instance=get_redis_connection(settings))
    return _client


async def init_redis(settings: ApplicationSettings | None = None) -> RedisClient:
    """Initialize Redis infrastructure during application startup.

    Args:
        settings: Optional application settings.

    Returns:
        The initialized RedisClient instance.
    """
    client = get_redis_client(settings)
    await client.ping()
    return client


async def close_redis() -> None:
    """Shutdown Redis infrastructure during application cleanup."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
    await close_redis_connection()


__all__ = [
    "RedisClient",
    "check_redis_health",
    "close_redis",
    "close_redis_connection",
    "get_redis_client",
    "get_redis_connection",
    "get_redis_pool",
    "init_redis",
]
