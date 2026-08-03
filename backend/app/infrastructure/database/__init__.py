"""PostgreSQL database infrastructure.

This package establishes the database connection layer of the backend:

- :mod:`app.infrastructure.database.engine` builds the async SQLAlchemy
  engine from the application settings.
- :mod:`app.infrastructure.database.session` provides the ``AsyncSession``
  factory, a reusable FastAPI dependency, and a context manager.
- :mod:`app.infrastructure.database.base` defines the declarative base that
  every SQLAlchemy ORM model will inherit from in the next phase.

No ORM models, Alembic configuration, repositories, or business logic exist
in this phase; this is connection infrastructure only.
"""

from app.infrastructure.database.base import Base
from app.infrastructure.database.engine import create_engine, get_engine
from app.infrastructure.database.session import (
    get_session,
    session_factory,
    session_scope,
)

__all__ = [
    "Base",
    "create_engine",
    "get_engine",
    "get_session",
    "session_factory",
    "session_scope",
]
