"""Reusable Redis client wrapper.

This module defines :class:`RedisClient`, a reusable wrapper around the
``redis.asyncio.Redis`` connection that exposes standard key-value operations
(get, set, delete, exists, expire, ping) without implementing any
business-specific logic.
"""

from __future__ import annotations

from typing import Any

from redis.asyncio import Redis

from app.infrastructure.cache.connection import get_redis_connection


class RedisClient:
    """Async Redis client wrapper exposing basic key-value primitives.

    Attributes:
        _redis: The underlying redis.asyncio.Redis instance.
    """

    def __init__(self, redis_instance: Redis[Any] | None = None) -> None:
        """Initialize the Redis client wrapper.

        Args:
            redis_instance: Optional Redis instance; if omitted, uses the shared
                connection instance.
        """
        self._redis = redis_instance or get_redis_connection()

    async def get(self, key: str) -> str | None:
        """Retrieve the string value of a key.

        Args:
            key: The key to look up.

        Returns:
            The string value if found, or None if the key does not exist.
        """
        result = await self._redis.get(key)
        if result is None:
            return None
        return str(result)

    async def set(
        self,
        key: str,
        value: str | bytes | int | float,
        expire_seconds: int | None = None,
        px: int | None = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """Set key to hold the string or numeric value.

        Args:
            key: The key to set.
            value: The value to store.
            expire_seconds: Time-to-live in seconds (EX parameter).
            px: Time-to-live in milliseconds (PX parameter).
            nx: Only set the key if it does not already exist.
            xx: Only set the key if it already exists.

        Returns:
            True if set operation succeeded, False otherwise.
        """
        res = await self._redis.set(
            name=key,
            value=value,
            ex=expire_seconds,
            px=px,
            nx=nx,
            xx=xx,
        )
        return bool(res)

    async def delete(self, *keys: str) -> int:
        """Delete one or more keys.

        Args:
            keys: The keys to delete.

        Returns:
            The number of keys removed.
        """
        if not keys:
            return 0
        return await self._redis.delete(*keys)

    async def exists(self, *keys: str) -> int:
        """Return the number of existing keys among the arguments.

        Args:
            keys: The keys to check.

        Returns:
            Number of keys that exist.
        """
        if not keys:
            return 0
        return await self._redis.exists(*keys)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set a timeout on key after which it will automatically be deleted.

        Args:
            key: The target key.
            seconds: Expiration timeout in seconds.

        Returns:
            True if the timeout was set, False if key does not exist.
        """
        return bool(await self._redis.expire(name=key, time=seconds))

    async def ping(self) -> bool:
        """Ping the Redis server to verify connectivity.

        Returns:
            True if server responds with PONG, False otherwise.
        """
        try:
            return bool(await self._redis.ping())
        except Exception:
            return False

    async def close(self) -> None:
        """Close the underlying client connection."""
        await self._redis.aclose()
