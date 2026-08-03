"""Qdrant connection and client management.

This module manages the asynchronous Qdrant vector database client connection
using ``qdrant_client.AsyncQdrantClient``. Connection parameters (URL) are
loaded from application settings (reading ``qdrant_url``).
"""

from __future__ import annotations

from qdrant_client import AsyncQdrantClient

from app.core.config import get_settings
from app.core.settings import ApplicationSettings

_client_instance: AsyncQdrantClient | None = None


def get_qdrant_client(settings: ApplicationSettings | None = None) -> AsyncQdrantClient:
    """Return the shared AsyncQdrantClient instance.

    Creates and caches an ``AsyncQdrantClient`` instance on first call using the
    ``qdrant_url`` specified in settings.

    Args:
        settings: Optional application settings. Defaults to loading from environment.

    Returns:
        The shared ``AsyncQdrantClient`` instance.
    """
    global _client_instance
    if _client_instance is None:
        cfg = settings or get_settings()
        url = cfg.qdrant_url or "http://localhost:6333"
        _client_instance = AsyncQdrantClient(url=url)
    return _client_instance


async def check_qdrant_health() -> bool:
    """Perform a health check ping against the Qdrant vector database.

    Returns:
        True if Qdrant responds, False otherwise.
    """
    try:
        client = get_qdrant_client()
        await client.get_collections()
        return True
    except Exception:
        return False


async def close_qdrant_client() -> None:
    """Close active AsyncQdrantClient connections and clear the cached instance."""
    global _client_instance
    if _client_instance is not None:
        await _client_instance.close()
        _client_instance = None
