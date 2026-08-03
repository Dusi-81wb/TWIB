"""Declarative base for SQLAlchemy ORM models.

This module defines the single ``DeclarativeBase`` subclass every ORM model
inherits from. It is deliberately empty in this phase: no ORM models exist
yet. The base exists now so that model definitions and Alembic
autogeneration can target a stable, shared base class in the next phase.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base class for all SQLAlchemy ORM models.

    Subclass this to define ORM models:

    .. code-block:: python

        class UserRow(Base):
            __tablename__ = "users"
            ...
    """
