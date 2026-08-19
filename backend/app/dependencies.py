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
from app.infrastructure.llm import LLMGateway, LLMProviderFactory
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
    session_service: SessionService = Depends(get_session_service),
) -> AuthenticationService:
    """Resolve the AuthenticationService instance from the DI container.

    Args:
        request: The active FastAPI request.
        uow: Request-scoped UnitOfWork dependency.
        session_service: Request-scoped SessionService dependency.

    Returns:
        An ``AuthenticationService`` instance bound to the request UnitOfWork
        and request SessionService.
    """
    container = get_container(request)
    return container.authentication_service(
        unit_of_work=uow,
        session_service=session_service,
    )


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
    settings: ApplicationSettings = Depends(get_settings),
) -> dict[str, Any]:
    """Decode and extract authenticated user claims from Authorization header.

    Supports both local TWIB JWTs and Supabase GoTrue Auth JWTs.

    Args:
        request: The active FastAPI request.
        jwt_helper: Injected JWTHelper dependency.
        settings: ApplicationSettings dependency.

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
    
    # 1. Try local TWIB JWT decode
    try:
        return jwt_helper.decode_token(token)
    except (InvalidTokenError, TokenExpiredError):
        pass

    # 2. Try Supabase JWT verification
    try:
        from app.security.supabase_auth import verify_supabase_jwt

        return verify_supabase_jwt(token, settings.supabase_jwt_secret)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired authentication token: {err}",
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
    workspace_service: WorkspaceService = Depends(get_workspace_service),
) -> InvitationService:
    """Resolve the InvitationService instance from the DI container.

    Args:
        request: The active FastAPI request.
        uow: Request-scoped UnitOfWork dependency.
        workspace_service: Request-scoped WorkspaceService dependency.

    Returns:
        An ``InvitationService`` instance bound to the request UnitOfWork.
    """
    container = get_container(request)
    return container.invitation_service(
        unit_of_work=uow,
        workspace_service=workspace_service,
    )


def get_llm_provider_factory(
    request: Request,
) -> LLMProviderFactory:
    """Resolve the LLMProviderFactory instance from the DI container.

    Args:
        request: The active FastAPI request.

    Returns:
        The singleton ``LLMProviderFactory`` instance.
    """
    container = get_container(request)
    return container.llm_provider_factory()


def get_llm_gateway(
    request: Request,
) -> LLMGateway:
    """Resolve the LLMGateway instance from the DI container.

    Args:
        request: The active FastAPI request.

    Returns:
        The singleton ``LLMGateway`` instance.
    """
    container = get_container(request)
    return container.llm_gateway()


def get_workflow_engine(request: Request) -> Any:
    """Resolve WorkflowEngine instance from the DI container."""
    return get_container(request).workflow_engine()


def get_workflow_executor(request: Request) -> Any:
    """Resolve WorkflowExecutor instance from the DI container."""
    return get_container(request).workflow_executor()


def get_workflow_state_manager(
    request: Request,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> Any:
    """Resolve WorkflowStateManager instance from the DI container."""
    return get_container(request).workflow_state_manager(uow=uow)


def get_workflow_template_service(request: Request) -> Any:
    """Resolve WorkflowTemplateService instance from the DI container."""
    return get_container(request).workflow_template_service()


def get_approval_manager(request: Request) -> Any:
    """Resolve ApprovalManager instance from the DI container."""
    return get_container(request).approval_manager()


def get_planner_agent(request: Request) -> Any:
    """Resolve PlannerAgent instance from the DI container."""
    return get_container(request).planner_agent()


def get_research_agent(request: Request) -> Any:
    """Resolve ResearchAgent instance from the DI container."""
    return get_container(request).research_agent()


def get_analyst_agent(request: Request) -> Any:
    """Resolve AnalystAgent instance from the DI container."""
    return get_container(request).analyst_agent()


def get_architect_agent(request: Request) -> Any:
    """Resolve ArchitectAgent instance from the DI container."""
    return get_container(request).architect_agent()


def get_validator_agent(request: Request) -> Any:
    """Resolve ValidatorAgent instance from the DI container."""
    return get_container(request).validator_agent()


def get_optimizer_agent(request: Request) -> Any:
    """Resolve OptimizerAgent instance from the DI container."""
    return get_container(request).optimizer_agent()


def get_documentation_agent(request: Request) -> Any:
    """Resolve DocumentationAgent instance from the DI container."""
    return get_container(request).documentation_agent()


def get_supervisor_agent(request: Request) -> Any:
    """Resolve SupervisorAgent instance from the DI container."""
    return get_container(request).supervisor_agent()


def get_websocket_manager(request: Request) -> Any:
    """Resolve WebSocketManager instance from the DI container."""
    return get_container(request).websocket_manager()


def get_workflow_event_publisher(request: Request) -> Any:
    """Resolve WorkflowEventPublisher instance from the DI container."""
    return get_container(request).workflow_event_publisher()


def get_monitoring_service(request: Request) -> Any:
    """Resolve MonitoringService instance from the DI container."""
    return get_container(request).monitoring_service()
