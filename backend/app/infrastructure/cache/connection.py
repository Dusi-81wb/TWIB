"""Redis connection and connection pool management.

This module provides async Redis connection pooling and client lifecycle
management using ``redis.asyncio``. The connection pool is configured from
application settings (reading ``redis_url``) and provides connection reuse,
health checking, and graceful shutdown.
"""

from __future__ import annotations

from redis.asyncio import ConnectionPool, Redis

from app.core.config import get_settings
from app.core.settings import ApplicationSettings

_pool: ConnectionPool | None = None
_client_instance: Redis | None = None


def get_redis_pool(settings: ApplicationSettings | None = None) -> ConnectionPool:
    """Return the application-wide async Redis connection pool.

    Creates and caches a ``ConnectionPool`` instance on first call using the
    ``redis_url`` specified in settings.

    Args:
        settings: Optional application settings. Defaults to loading from environment.

    Returns:
        The shared ``ConnectionPool`` instance.
    """
    global _pool
    if _pool is None:
        cfg = settings or get_settings()
        url = cfg.redis_url or "redis://localhost:6379/0"
        _pool = ConnectionPool.from_url(
            url,
            decode_responses=True,
            max_connections=20,
        )
    return _pool


def get_redis_connection(settings: ApplicationSettings | None = None) -> Redis:
    """Return the shared async Redis connection client.

    Creates and caches a ``Redis`` client instance bound to the shared
    connection pool on first call.

    Args:
        settings: Optional application settings.

    Returns:
        The shared async ``Redis`` client instance.
    """
    global _client_instance
    if _client_instance is None:
        pool = get_redis_pool(settings)
        _client_instance = Redis(connection_pool=pool)
    return _client_instance


async def check_redis_health() -> bool:
    """Perform a ping health check against Redis.

    Returns:
        True if Redis responds to PING, False otherwise.
    """
    try:
        client = get_redis_connection()
        return bool(await client.ping())
    except Exception:
        return False


async def close_redis_connection() -> None:
    """Close active Redis connections and dispose of the connection pool."""
    global _pool, _client_instance
    if _client_instance is not None:
        await _client_instance.aclose()
        _client_instance = None
    if _pool is not None:
        await _pool.aclose()
        _pool = None
