"""Qdrant vector database infrastructure package.

Provides connection management, collection helpers, and a reusable
VectorStoreClient wrapper:

- :class:`~app.infrastructure.vector.client.VectorStoreClient`:
  Client wrapper for vector storage and search.
- :func:`~app.infrastructure.vector.connection.get_qdrant_client`:
  Singleton provider for AsyncQdrantClient.
- :func:`~app.infrastructure.vector.connection.check_qdrant_health`:
  Health check helper.
- :func:`~app.infrastructure.vector.connection.close_qdrant_client`:
  Connection cleanup helper.
"""

from __future__ import annotations

from app.core.settings import ApplicationSettings
from app.infrastructure.vector.client import VectorStoreClient
from app.infrastructure.vector.collections import (
    collection_exists,
    create_collection,
    delete_collection,
    list_collections,
)
from app.infrastructure.vector.connection import (
    check_qdrant_health,
    close_qdrant_client,
    get_qdrant_client,
)

_vector_client: VectorStoreClient | None = None


def get_vector_store_client(
    settings: ApplicationSettings | None = None,
) -> VectorStoreClient:
    """Return the shared VectorStoreClient instance.

    Args:
        settings: Optional application settings.

    Returns:
        The cached VectorStoreClient instance.
    """
    global _vector_client
    if _vector_client is None:
        _vector_client = VectorStoreClient(qdrant_instance=get_qdrant_client(settings))
    return _vector_client


async def init_vector_store(
    settings: ApplicationSettings | None = None,
) -> VectorStoreClient:
    """Initialize vector store infrastructure during application startup.

    Args:
        settings: Optional application settings.

    Returns:
        The initialized VectorStoreClient instance.
    """
    client = get_vector_store_client(settings)
    await client.ping()
    return client


async def close_vector_store() -> None:
    """Shutdown vector store infrastructure during application cleanup."""
    global _vector_client
    if _vector_client is not None:
        await _vector_client.close()
        _vector_client = None
    await close_qdrant_client()


__all__ = [
    "VectorStoreClient",
    "check_qdrant_health",
    "close_qdrant_client",
    "close_vector_store",
    "collection_exists",
    "create_collection",
    "delete_collection",
    "get_qdrant_client",
    "get_vector_store_client",
    "init_vector_store",
    "list_collections",
]
