"""Base ORM model for SQLAlchemy 2.0 entities.

This module defines :class:`BaseModel`, the abstract base class that every
SQLAlchemy ORM model in TWIB inherits from. It builds on the shared
declarative base (:class:`app.infrastructure.database.base.Base`) and
provides standard audit columns:

- ``id``: Primary key UUID, auto-generated via ``uuid.uuid4``.
- ``created_at``: Creation timestamp in UTC timezone.
- ``updated_at``: Last update timestamp in UTC timezone, automatically
  refreshed on modification.
- ``version``: Optimistic-locking integer counter (defaults to 0).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class BaseModel(Base):
    """Abstract base model with common audit columns.

    All concrete ORM models inherit from this class to ensure consistent
    primary keys, creation/update timestamps, and optimistic locking fields.

    Attributes:
        id: The primary key UUID.
        created_at: Moment when the record was inserted (UTC).
        updated_at: Moment when the record was last modified (UTC).
        version: Optimistic-locking version integer counter.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Return a readable representation of the ORM model instance."""
        return f"<{type(self).__name__}(id={self.id})>"
