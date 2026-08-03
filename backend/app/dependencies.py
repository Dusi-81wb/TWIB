"""FastAPI dependency functions backed by the dependency injection container.

Every function resolves its object from the application container stored on
``app.state.container`` instead of creating module-level singletons. This
keeps the object graph owned by a single place and makes overrides in tests
straightforward.
"""

from collections.abc import AsyncIterator
from typing import cast

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import BoundLogger

from app.container import ApplicationContainer
from app.core.settings import ApplicationSettings
from app.domain.repositories.unit_of_work import UnitOfWork
from app.infrastructure.cache import RedisClient
from app.infrastructure.database.session import get_session
from app.infrastructure.vector import VectorStoreClient


def get_container(request: Request) -> ApplicationContainer:
    """Return the application dependency injection container.

    Args:
        request: The active FastAPI request.

    Returns:
        The application's ``ApplicationContainer`` instance.
    """
    return cast(ApplicationContainer, request.app.state.container)


def get_settings(request: Request) -> ApplicationSettings:
    """Resolve the application settings from the DI container.

    Args:
        request: The active FastAPI request.

    Returns:
        The shared ``ApplicationSettings`` singleton.
    """
    return get_container(request).settings()


def get_logger(request: Request, name: str = "app") -> BoundLogger:
    """Resolve a named structured logger from the DI container.

    Args:
        request: The active FastAPI request.
        name: Logger name, typically the calling module ``__name__``.

    Returns:
        A structlog logger bound to the given name.
    """
    return get_container(request).logger(name=name)


async def get_unit_of_work(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> AsyncIterator[UnitOfWork]:
    """Resolve a session-bound Unit of Work from the DI container.

    Args:
        request: The active FastAPI request.
        session: The request-scoped AsyncSession dependency.

    Yields:
        A session-bound ``UnitOfWork`` instance.
    """
    uow: UnitOfWork = get_container(request).unit_of_work(session=session)
    try:
        yield uow
    finally:
        await uow.close()


def get_redis_client(request: Request) -> RedisClient:
    """Resolve the RedisClient instance from the DI container.

    Args:
        request: The active FastAPI request.

    Returns:
        The ``RedisClient`` instance.
    """
    return get_container(request).redis_client()


def get_vector_store_client(request: Request) -> VectorStoreClient:
    """Resolve the VectorStoreClient instance from the DI container.

    Args:
        request: The active FastAPI request.

    Returns:
        The ``VectorStoreClient`` instance.
    """
    return get_container(request).vector_client()
