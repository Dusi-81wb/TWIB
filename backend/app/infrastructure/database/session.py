"""Async SQLAlchemy sessions for PostgreSQL.

This module provides the session layer of the database infrastructure:

- :func:`session_factory` builds the ``async_sessionmaker`` bound to the
  application engine.
- :func:`get_session` is the reusable FastAPI dependency that yields a
  request-scoped ``AsyncSession``.
- :func:`session_scope` is a context manager that opens a session and
  commits (or rolls back) automatically.

Sessions are configured with ``expire_on_commit=False`` so that aggregate
instances remain usable after a commit, and with ``autoflush=False`` so
that the unit of work controls exactly when changes are sent to the
database.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.database.engine import get_engine


@lru_cache(maxsize=1)
def session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the cached async session factory.

    The factory is bound to the shared application engine and produces
    ``AsyncSession`` objects for one logical transaction each. It is cached
    so every caller shares the same factory.

    Returns:
        The shared ``async_sessionmaker`` for ``AsyncSession``.
    """
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped async session.

    Reusable FastAPI dependency. Each request obtains its own session from
    the shared factory and is guaranteed to be closed when the request
    finishes, regardless of errors.

    Yields:
        An open ``AsyncSession`` for the current request.
    """
    async with session_factory()() as session:
        yield session


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """Open a session and commit it on success.

    Context manager that creates a session, yields it to the caller, and
    then commits on a clean exit or rolls back and re-raises when the body
    raises. The session is always closed, even on errors.

    Yields:
        An open ``AsyncSession`` scoped to the ``async with`` block.
    """
    async with session_factory()() as session:
        try:
            yield session
            await session.commit()
        except BaseException:
            await session.rollback()
            raise
