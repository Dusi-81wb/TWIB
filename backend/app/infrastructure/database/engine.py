"""Async SQLAlchemy engine for PostgreSQL and SQLite.

This module builds the SQLAlchemy 2.0 async engine used by the whole
application. The engine is configured from the application settings (the
``database_url`` connection string) and provides connection pooling with
pool pre-ping so stale connections are detected and replaced before they
are handed out.

Debug logging is enabled only when ``DEBUG`` is ``True``: SQLAlchemy echo
turns on the emitted SQL statements, which is noisy and must never run in
production.

The engine is a long-lived process-wide resource. :func:`get_engine` caches
the single engine instance so every session factory and repository shares
one connection pool.
"""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.core.settings import ApplicationSettings

_POOL_SIZE = 5
_MAX_OVERFLOW = 10


def create_engine(settings: ApplicationSettings) -> AsyncEngine:
    """Create the async SQLAlchemy engine from application settings.

    Args:
        settings: The application settings providing ``database_url`` and
            ``debug``.

    Returns:
        A configured async engine.
    """
    db_url = settings.database_url or "sqlite+aiosqlite:///./twib.db"

    if db_url.startswith("sqlite"):
        return create_async_engine(
            db_url,
            echo=settings.debug,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    return create_async_engine(
        db_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=_POOL_SIZE,
        max_overflow=_MAX_OVERFLOW,
    )


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Return the cached application-wide async engine.

    Returns:
        The shared ``AsyncEngine`` instance.
    """
    return create_engine(get_settings())
