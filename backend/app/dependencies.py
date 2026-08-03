"""FastAPI dependency functions backed by the dependency injection container.

Every function resolves its object from the application container stored on
``app.state.container`` instead of creating module-level singletons. This
keeps the object graph owned by a single place and makes overrides in tests
straightforward.
"""

from collections.abc import AsyncIterator
from typing import Any, cast

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import BoundLogger

from app.authorization.authorization_service import AuthorizationService
from app.container import ApplicationContainer
from app.core.settings import ApplicationSettings
from app.domain.repositories.unit_of_work import UnitOfWork
from app.infrastructure.cache import RedisClient
from app.infrastructure.database.session import get_session
from app.infrastructure.vector import VectorStoreClient
from app.security import JWTHelper, PasswordHasher
from app.security.exceptions import InvalidTokenError, TokenExpiredError
from app.services.api_keys import ApiKeyService
from app.services.audit import AuditService
from app.services.auth import AuthenticationService, SessionService
from app.services.invitations import InvitationService
from app.services.organizations import OrganizationService
from app.services.users import UserService
from app.services.workspaces import WorkspaceService


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


def get_password_hasher(request: Request) -> PasswordHasher:
    """Resolve the PasswordHasher instance from the DI container.

    Args:
        request: The active FastAPI request.

    Returns:
        The ``PasswordHasher`` singleton instance.
    """
    return get_container(request).password_hasher()


def get_jwt_helper(request: Request) -> JWTHelper:
    """Resolve the JWTHelper instance from the DI container.

    Args:
        request: The active FastAPI request.

    Returns:
        The ``JWTHelper`` instance.
    """
    return get_container(request).jwt_helper()


def get_session_service(
    request: Request,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> SessionService:
    """Resolve the SessionService instance from the DI container.

    Args:
        request: The active FastAPI request.
        uow: Request-scoped UnitOfWork dependency.

    Returns:
        A ``SessionService`` instance bound to the request UnitOfWork.
    """
    container = get_container(request)
    return container.session_service(unit_of_work=uow)


def get_authentication_service(
    request: Request,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> AuthenticationService:
    """Resolve the AuthenticationService instance from the DI container.

    Args:
        request: The active FastAPI request.
        uow: Request-scoped UnitOfWork dependency.

    Returns:
        An ``AuthenticationService`` instance bound to the request UnitOfWork.
    """
    container = get_container(request)
    return container.authentication_service(unit_of_work=uow)


def get_authorization_service(
    request: Request,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> AuthorizationService:
    """Resolve the AuthorizationService instance from the DI container.

    Args:
        request: The active FastAPI request.
        uow: Request-scoped UnitOfWork dependency.

    Returns:
        An ``AuthorizationService`` instance bound to the request UnitOfWork.
    """
    container = get_container(request)
    return container.authorization_service(unit_of_work=uow)


def get_api_key_service(request: Request) -> ApiKeyService:
    """Resolve the ApiKeyService instance from the DI container.

    Args:
        request: The active FastAPI request.

    Returns:
        The ``ApiKeyService`` singleton instance.
    """
    return get_container(request).api_key_service()


def get_audit_service(request: Request) -> AuditService:
    """Resolve the AuditService instance from the DI container.

    Args:
        request: The active FastAPI request.

    Returns:
        The ``AuditService`` singleton instance.
    """
    return get_container(request).audit_service()


def get_current_user_claims(
    request: Request,
    jwt_helper: JWTHelper = Depends(get_jwt_helper),
) -> dict[str, Any]:
    """Decode and extract authenticated user claims from Authorization header.

    Args:
        request: The active FastAPI request.
        jwt_helper: Injected JWTHelper dependency.

    Returns:
        Dictionary of token claims containing sub (user_id), email, role, etc.

    Raises:
        HTTPException: 401 Unauthorized if header or token is invalid.
    """
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ", 1)[1].strip()
    try:
        return jwt_helper.decode_token(token)
    except (InvalidTokenError, TokenExpiredError) as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


def get_user_service(
    request: Request,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> UserService:
    """Resolve the UserService instance from the DI container.

    Args:
        request: The active FastAPI request.
        uow: Request-scoped UnitOfWork dependency.

    Returns:
        A ``UserService`` instance bound to the request UnitOfWork.
    """
    container = get_container(request)
    return container.user_service(unit_of_work=uow)


def get_organization_service(
    request: Request,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> OrganizationService:
    """Resolve the OrganizationService instance from the DI container.

    Args:
        request: The active FastAPI request.
        uow: Request-scoped UnitOfWork dependency.

    Returns:
        An ``OrganizationService`` instance bound to the request UnitOfWork.
    """
    container = get_container(request)
    return container.organization_service(unit_of_work=uow)


def get_workspace_service(
    request: Request,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> WorkspaceService:
    """Resolve the WorkspaceService instance from the DI container.

    Args:
        request: The active FastAPI request.
        uow: Request-scoped UnitOfWork dependency.

    Returns:
        A ``WorkspaceService`` instance bound to the request UnitOfWork.
    """
    container = get_container(request)
    return container.workspace_service(unit_of_work=uow)


def get_invitation_service(
    request: Request,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> InvitationService:
    """Resolve the InvitationService instance from the DI container.

    Args:
        request: The active FastAPI request.
        uow: Request-scoped UnitOfWork dependency.

    Returns:
        An ``InvitationService`` instance bound to the request UnitOfWork.
    """
    container = get_container(request)
    return container.invitation_service(unit_of_work=uow)
