"""FastAPI dependency functions backed by the dependency injection container.

Every function resolves its object from the application container stored on
``app.state.container`` instead of creating module-level singletons. This
keeps the object graph owned by a single place and makes overrides in tests
straightforward.
"""

from typing import cast

from fastapi import Request
from structlog import BoundLogger

from app.container import ApplicationContainer
from app.core.settings import ApplicationSettings


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
