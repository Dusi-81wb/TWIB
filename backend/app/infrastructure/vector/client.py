"""Reusable Vector Store client wrapper.

This module defines :class:`VectorStoreClient`, a reusable wrapper around
``qdrant_client.AsyncQdrantClient`` that exposes generic vector operations
(upsert, search, delete, get, ping, collection management) without any
domain-specific or LLM/RAG logic.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct

from app.infrastructure.vector.collections import (
    collection_exists as _collection_exists,
)
from app.infrastructure.vector.collections import (
    create_collection as _create_collection,
)
from app.infrastructure.vector.collections import (
    delete_collection as _delete_collection,
)
from app.infrastructure.vector.collections import (
    list_collections as _list_collections,
)
from app.infrastructure.vector.connection import get_qdrant_client


class VectorStoreClient:
    """Async Vector Store client wrapper for Qdrant.

    Exposes generic vector storage, retrieval, search, and collection management
    methods.

    Attributes:
        _qdrant: The underlying AsyncQdrantClient instance.
    """

    def __init__(self, qdrant_instance: AsyncQdrantClient | None = None) -> None:
        """Initialize the Vector Store client wrapper.

        Args:
            qdrant_instance: Optional AsyncQdrantClient instance; if omitted,
                uses the shared connection instance.
        """
        self._qdrant = qdrant_instance or get_qdrant_client()

    async def collection_exists(self, name: str) -> bool:
        """Check whether a collection exists.

        Args:
            name: Collection name.

        Returns:
            True if present, False otherwise.
        """
        return await _collection_exists(self._qdrant, name)

    async def create_collection(
        self,
        name: str,
        vector_size: int = 1536,
        distance: str = "Cosine",
    ) -> bool:
        """Create a vector collection.

        Args:
            name: Collection name.
            vector_size: Dimensionality of vectors.
            distance: Similarity distance metric.

        Returns:
            True if created or already exists, False on failure.
        """
        return await _create_collection(
            self._qdrant, name, vector_size=vector_size, distance=distance
        )

    async def delete_collection(self, name: str) -> bool:
        """Delete a vector collection.

        Args:
            name: Collection name.

        Returns:
            True if deleted or nonexistent, False on failure.
        """
        return await _delete_collection(self._qdrant, name)

    async def list_collections(self) -> list[str]:
        """List all collection names.

        Returns:
            List of collection name strings.
        """
        return await _list_collections(self._qdrant)

    async def upsert_points(
        self,
        collection_name: str,
        points: list[PointStruct | dict[str, Any]],
    ) -> bool:
        """Upsert vector points into a collection.

        Args:
            collection_name: Target collection name.
            points: List of PointStruct instances or point dicts.

        Returns:
            True if upsert succeeded, False otherwise.
        """
        if not points:
            return True

        point_structs: list[PointStruct] = []
        for p in points:
            if isinstance(p, PointStruct):
                point_structs.append(p)
            elif isinstance(p, dict):
                point_structs.append(
                    PointStruct(
                        id=p["id"],
                        vector=p["vector"],
                        payload=p.get("payload", {}),
                    )
                )

        try:
            await self._qdrant.upsert(
                collection_name=collection_name,
                points=point_structs,
            )
            return True
        except Exception:
            return False

    async def search_points(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 10,
        score_threshold: float | None = None,
    ) -> list[Any]:
        """Perform a similarity vector search.

        Args:
            collection_name: Target collection name.
            query_vector: Query embedding vector.
            limit: Maximum number of search results.
            score_threshold: Minimum similarity score threshold.

        Returns:
            List of matching ScoredPoint instances.
        """
        try:
            return list(
                await self._qdrant.search(  # type: ignore[attr-defined]
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=limit,
                    score_threshold=score_threshold,
                )
            )
        except Exception:
            return []

    async def get_point(
        self,
        collection_name: str,
        point_id: str | int,
    ) -> Any | None:
        """Retrieve a single point by ID.

        Args:
            collection_name: Target collection name.
            point_id: ID of the point to retrieve.

        Returns:
            The Record object if found, None otherwise.
        """
        try:
            records = await self._qdrant.retrieve(
                collection_name=collection_name,
                ids=[point_id],
            )
            if records:
                return records[0]
            return None
        except Exception:
            return None

    async def delete_points(
        self,
        collection_name: str,
        point_ids: Sequence[str | int],
    ) -> bool:
        """Delete points by ID from a collection.

        Args:
            collection_name: Target collection name.
            point_ids: List of point IDs to delete.

        Returns:
            True if deletion request succeeded, False otherwise.
        """
        if not point_ids:
            return True

        try:
            await self._qdrant.delete(
                collection_name=collection_name,
                points_selector=cast(Any, list(point_ids)),
            )
            return True
        except Exception:
            return False

    async def ping(self) -> bool:
        """Ping the Qdrant database to verify connectivity.

        Returns:
            True if Qdrant responds, False otherwise.
        """
        try:
            await self._qdrant.get_collections()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close the underlying client connection."""
        await self._qdrant.close()
