"""Application dependency injection container.

The container is built with ``dependency-injector`` and owns the object
graph of the application. Every dependency is resolved through a provider,
so components never instantiate their collaborators directly.

Currently registered providers:

- ``settings``: the application configuration singleton.
- ``logger``: a factory that returns named structured loggers.

Future services, repositories, and infrastructure adapters will be
registered here as additional providers.
"""

from dependency_injector import containers, providers

from app.core.config import get_settings as _load_settings
from app.core.logging import get_logger as _resolve_logger


class ApplicationContainer(containers.DeclarativeContainer):
    """Declarative dependency injection container for the TWIB backend.

    The container is created and initialized by the application factory
    and exposed to every component through ``app.state.container``.

    Attributes:
        settings: Singleton provider resolving the application settings.
        logger: Factory provider building named structured loggers.
    """

    settings = providers.Singleton(_load_settings)
    logger = providers.Factory(_resolve_logger)
