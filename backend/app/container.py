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

from app.authorization.authorization_service import AuthorizationService
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
from app.security import JWTHelper, PasswordHasher
from app.services.api_keys import ApiKeyService
from app.services.audit import AuditService
from app.services.auth import AuthenticationService, SessionService
from app.services.invitations import InvitationService
from app.services.organizations import OrganizationService
from app.services.users import UserService
from app.services.workspaces import WorkspaceService


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
        password_hasher: Singleton provider returning PasswordHasher.
        jwt_helper: Factory provider returning JWTHelper.
        session_service: Factory provider returning SessionService.
        authentication_service: Factory provider returning AuthenticationService.
        authorization_service: Factory provider returning AuthorizationService.
        api_key_service: Singleton provider returning ApiKeyService.
        audit_service: Singleton provider returning AuditService.
        user_service: Factory provider returning UserService.
    """

    settings = providers.Singleton(_load_settings)
    logger = providers.Factory(_resolve_logger)

    user_repository = providers.Factory(SQLAlchemyUserRepository)
    organization_repository = providers.Factory(SQLAlchemyOrganizationRepository)
    workspace_repository = providers.Factory(SQLAlchemyWorkspaceRepository)
    unit_of_work = providers.Factory(SQLAlchemyUnitOfWork)
    redis_client = providers.Factory(_resolve_redis_client)
    vector_client = providers.Factory(_resolve_vector_store_client)
    password_hasher = providers.Singleton(PasswordHasher)
    jwt_helper = providers.Factory(JWTHelper, settings=settings)
    session_service = providers.Factory(
        SessionService,
        redis_client=redis_client,
        unit_of_work=unit_of_work,
        jwt_helper=jwt_helper,
        settings=settings,
    )
    authentication_service = providers.Factory(
        AuthenticationService,
        unit_of_work=unit_of_work,
        password_hasher=password_hasher,
        jwt_helper=jwt_helper,
        settings=settings,
        session_service=session_service,
    )
    authorization_service = providers.Factory(
        AuthorizationService,
        unit_of_work=unit_of_work,
    )
    api_key_service = providers.Singleton(ApiKeyService)
    audit_service = providers.Singleton(AuditService)
    user_service = providers.Factory(
        UserService,
        unit_of_work=unit_of_work,
    )
    organization_service = providers.Factory(
        OrganizationService,
        unit_of_work=unit_of_work,
    )
    workspace_service = providers.Factory(
        WorkspaceService,
        unit_of_work=unit_of_work,
    )
    invitation_service = providers.Factory(
        InvitationService,
        unit_of_work=unit_of_work,
        workspace_service=workspace_service,
    )
