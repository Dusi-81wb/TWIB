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

from app.agents import (
    AnalystAgent,
    ArchitectAgent,
    DocumentationAgent,
    OptimizerAgent,
    PlannerAgent,
    ResearchAgent,
    SupervisorAgent,
    ValidatorAgent,
)
from app.authorization.authorization_service import AuthorizationService
from app.core.config import get_settings as _load_settings
from app.core.logging import get_logger as _resolve_logger
from app.infrastructure.cache import get_redis_client as _resolve_redis_client
from app.infrastructure.llm import LLMProviderFactory, OmniRouteGateway
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
from app.services.monitoring_service import MonitoringService
from app.services.organizations import OrganizationService
from app.services.users import UserService
from app.services.workspaces import WorkspaceService
from app.workflows import (
    ApprovalManager,
    WebSocketManager,
    WorkflowEngine,
    WorkflowEventPublisher,
    WorkflowExecutor,
    WorkflowStateManager,
    WorkflowTemplateService,
)
from app.workflows.workflow_monitor import WorkflowMonitor


class ApplicationContainer(containers.DeclarativeContainer):
    """Declarative dependency injection container for the TWIB backend.

    The container is created and initialized by the application factory
    and exposed to every component through ``app.state.container``.
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
    llm_provider_factory = providers.Singleton(
        LLMProviderFactory,
        settings=settings,
    )
    llm_gateway = providers.Singleton(
        OmniRouteGateway,
        settings=settings,
    )
    planner_agent = providers.Factory(
        PlannerAgent,
        llm_factory=llm_provider_factory,
    )
    research_agent = providers.Factory(
        ResearchAgent,
        llm_gateway=llm_gateway,
        llm_factory=llm_provider_factory,
    )
    analyst_agent = providers.Factory(
        AnalystAgent,
        llm_factory=llm_provider_factory,
    )
    architect_agent = providers.Factory(
        ArchitectAgent,
        llm_factory=llm_provider_factory,
    )
    validator_agent = providers.Factory(
        ValidatorAgent,
        llm_factory=llm_provider_factory,
    )
    optimizer_agent = providers.Factory(
        OptimizerAgent,
        llm_factory=llm_provider_factory,
    )
    documentation_agent = providers.Factory(
        DocumentationAgent,
        llm_factory=llm_provider_factory,
    )
    supervisor_agent = providers.Factory(
        SupervisorAgent,
        llm_factory=llm_provider_factory,
    )
    workflow_event_publisher = providers.Singleton(WorkflowEventPublisher)
    websocket_manager = providers.Singleton(WebSocketManager)
    workflow_engine = providers.Singleton(WorkflowEngine)
    workflow_executor = providers.Singleton(
        WorkflowExecutor,
        engine=workflow_engine,
    )
    workflow_state_manager = providers.Singleton(
        WorkflowStateManager,
        uow=unit_of_work,
    )
    workflow_template_service = providers.Singleton(
        WorkflowTemplateService,
        engine=workflow_engine,
        audit_service=audit_service,
    )
    workflow_monitor = providers.Factory(
        WorkflowMonitor,
        engine=workflow_engine,
    )
    monitoring_service = providers.Factory(
        MonitoringService,
        engine=workflow_engine,
        llm_factory=llm_provider_factory,
        monitor=workflow_monitor,
    )
    approval_manager = providers.Singleton(
        ApprovalManager,
        engine=workflow_engine,
        state_manager=workflow_state_manager,
        audit_service=audit_service,
    )
