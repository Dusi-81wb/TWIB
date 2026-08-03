"""Generic SQLAlchemy repository base.

This module provides :class:`BaseRepository`, an abstract class for concrete
SQLAlchemy repository implementations. It provides common async CRUD helpers,
session management, and abstract domain mapping hooks (:meth:`_to_domain` and
:meth:`_to_model`).
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entity import Entity
from app.infrastructure.database.models.base_model import BaseModel


class BaseRepository[
    TEntity: Entity[Any],
    TModel: BaseModel,
    TID: uuid.UUID | str | int,
](ABC):
    """Abstract base repository for SQLAlchemy 2.0 async sessions.

    Wraps common aggregate persistence operations (lookup by ID, existence check,
    saving, and deletion) using the provided AsyncSession and ORM model.

    Attributes:
        _session: The active AsyncSession for database operations.
        _model_class: The concrete BaseModel class backing this repository.
    """

    def __init__(self, session: AsyncSession, model_class: type[TModel]) -> None:
        """Initialize the repository.

        Args:
            session: The active AsyncSession.
            model_class: The ORM model class.
        """
        self._session = session
        self._model_class = model_class

    @abstractmethod
    def _to_domain(self, model: TModel) -> TEntity:
        """Convert a persistent ORM model instance into a domain aggregate root.

        Args:
            model: The ORM model to map.

        Returns:
            The reconstructed domain aggregate root.
        """
        ...

    @abstractmethod
    def _to_model(self, entity: TEntity, existing: TModel | None = None) -> TModel:
        """Convert a domain aggregate root into an ORM model instance.

        Args:
            entity: The domain aggregate root.
            existing: Optional existing ORM model to update in-place.

        Returns:
            The populated ORM model instance.
        """
        ...

    async def get_by_id(self, id_: TID) -> TEntity | None:
        """Load an aggregate root by its primary key identity.

        Args:
            id_: The identity value.

        Returns:
            The domain aggregate root, or None if not found.
        """
        raw_id = id_.value if hasattr(id_, "value") else id_
        model = await self._session.get(self._model_class, raw_id)
        if model is None:
            return None
        return self._to_domain(model)

    async def exists(self, id_: TID) -> bool:
        """Check whether an aggregate root exists by identity.

        Args:
            id_: The identity value.

        Returns:
            True if present in database, False otherwise.
        """
        raw_id = id_.value if hasattr(id_, "value") else id_
        stmt = select(self._model_class.id).where(self._model_class.id == raw_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def save(self, entity: TEntity) -> None:
        """Persist an aggregate root, inserting or updating as needed.

        Args:
            entity: The aggregate root to save.
        """
        raw_id = entity.id.value if hasattr(entity.id, "value") else entity.id
        existing = await self._session.get(self._model_class, raw_id)
        model = self._to_model(entity, existing=existing)
        if existing is None:
            self._session.add(model)

    async def delete(self, id_: TID) -> None:
        """Delete an aggregate root by identity.

        Args:
            id_: The identity of the aggregate to remove.
        """
        raw_id = id_.value if hasattr(id_, "value") else id_
        existing = await self._session.get(self._model_class, raw_id)
        if existing is not None:
            await self._session.delete(existing)
