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
from app.infrastructure.cache import get_redis_client as _resolve_redis_client
from app.infrastructure.repositories import (
    SQLAlchemyOrganizationRepository,
    SQLAlchemyUnitOfWork,
    SQLAlchemyUserRepository,
    SQLAlchemyWorkspaceRepository,
)
from app.infrastructure.vector import (
    get_vector_store_client as _resolve_vector_store_client,
)


class ApplicationContainer(containers.DeclarativeContainer):
    """Declarative dependency injection container for the TWIB backend.

    The container is created and initialized by the application factory
    and exposed to every component through ``app.state.container``.

    Attributes:
        settings: Singleton provider resolving the application settings.
        logger: Factory provider building named structured loggers.
        user_repository: Factory provider building User repositories.
        organization_repository: Factory provider building Organization repositories.
        workspace_repository: Factory provider building Workspace repositories.
        unit_of_work: Factory provider building Unit of Work instances.
        redis_client: Factory provider returning the RedisClient instance.
        vector_client: Factory provider returning the VectorStoreClient instance.
    """

    settings = providers.Singleton(_load_settings)
    logger = providers.Factory(_resolve_logger)

    user_repository = providers.Factory(SQLAlchemyUserRepository)
    organization_repository = providers.Factory(SQLAlchemyOrganizationRepository)
    workspace_repository = providers.Factory(SQLAlchemyWorkspaceRepository)
    unit_of_work = providers.Factory(SQLAlchemyUnitOfWork)
    redis_client = providers.Factory(_resolve_redis_client)
    vector_client = providers.Factory(_resolve_vector_store_client)
