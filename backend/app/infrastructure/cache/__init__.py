"""Redis cache infrastructure package.

Provides connection pooling, lifecycle management, and a reusable Redis client
wrapper:

- :class:`~app.infrastructure.cache.client.RedisClient`:
  Client wrapper for key-value operations.
- :func:`~app.infrastructure.cache.redis.get_redis_client`:
  Singleton provider for RedisClient.
- :func:`~app.infrastructure.cache.redis.init_redis`: Startup initializer.
- :func:`~app.infrastructure.cache.redis.close_redis`: Graceful shutdown cleaner.
"""

from app.infrastructure.cache.client import RedisClient
from app.infrastructure.cache.connection import (
    check_redis_health,
    close_redis_connection,
    get_redis_pool,
)
from app.infrastructure.cache.redis import (
    close_redis,
    get_redis_client,
    init_redis,
)

__all__ = [
    "RedisClient",
    "check_redis_health",
    "close_redis",
    "close_redis_connection",
    "get_redis_client",
    "get_redis_pool",
    "init_redis",
]
