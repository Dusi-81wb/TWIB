"""Qdrant vector collection management helpers.

This module provides reusable collection management functions (create, delete,
check existence, list) for Qdrant vector spaces using ``AsyncQdrantClient``.
No collections are created automatically during import or initialization.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qdrant_client.models import Distance, VectorParams

if TYPE_CHECKING:
    from qdrant_client import AsyncQdrantClient


def _parse_distance(distance_str: str) -> Distance:
    """Parse distance string metric into Qdrant Distance enum.

    Args:
        distance_str: Distance metric name (e.g. Cosine, Dot, Euclidean).

    Returns:
        The matching Qdrant Distance enum value.
    """
    normalized = distance_str.upper().strip()
    if normalized == "DOT":
        return Distance.DOT
    if normalized in ("EUCLID", "EUCLIDEAN"):
        return Distance.EUCLID
    return Distance.COSINE


async def collection_exists(client: AsyncQdrantClient, name: str) -> bool:
    """Check whether a collection exists in Qdrant.

    Args:
        client: Active AsyncQdrantClient instance.
        name: Name of the collection.

    Returns:
        True if the collection exists, False otherwise.
    """
    try:
        return bool(await client.collection_exists(collection_name=name))
    except Exception:
        return False


async def create_collection(
    client: AsyncQdrantClient,
    name: str,
    vector_size: int = 1536,
    distance: str = "Cosine",
) -> bool:
    """Create a new vector collection in Qdrant if it does not exist.

    Args:
        client: Active AsyncQdrantClient instance.
        name: Name of the collection to create.
        vector_size: Dimensionality of vectors stored in the collection.
        distance: Distance metric used for similarity search (Cosine, Dot, Euclid).

    Returns:
        True if creation succeeded, False otherwise.
    """
    if await collection_exists(client, name):
        return True

    distance_enum = _parse_distance(distance)
    vector_config = VectorParams(size=vector_size, distance=distance_enum)
    try:
        return bool(
            await client.create_collection(
                collection_name=name,
                vectors_config=vector_config,
            )
        )
    except Exception:
        return False


async def delete_collection(client: AsyncQdrantClient, name: str) -> bool:
    """Delete a vector collection from Qdrant.

    Args:
        client: Active AsyncQdrantClient instance.
        name: Name of the collection to delete.

    Returns:
        True if deletion succeeded, False otherwise.
    """
    if not await collection_exists(client, name):
        return True

    try:
        return bool(await client.delete_collection(collection_name=name))
    except Exception:
        return False


async def list_collections(client: AsyncQdrantClient) -> list[str]:
    """List names of all vector collections in Qdrant.

    Args:
        client: Active AsyncQdrantClient instance.

    Returns:
        List of collection names.
    """
    try:
        response = await client.get_collections()
        return [c.name for c in response.collections]
    except Exception:
        return []
