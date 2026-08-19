"""Agent REST API router for v1 endpoints.

Exposes REST API endpoints for agent execution across all 8 specialized agents,
and synchronous LLM gateway run/conversation endpoints.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.agent_dag import AgentDAGPlan, DAGExecutionResult
from app.agents.analyst_agent import AnalystAgent
from app.agents.architect_agent import ArchitectAgent
from app.agents.base_agent import BaseAgent
from app.agents.documentation_agent import DocumentationAgent
from app.agents.exceptions import (
    AgentError,
    AgentExecutionError,
    AgentValidationError,
)
from app.agents.models import AgentRequest, AgentResponse
from app.agents.optimizer_agent import OptimizerAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.agents.validator_agent import ValidatorAgent
from app.api.openapi import COMMON_RESPONSES
from app.api.tags import AGENTS
from app.dependencies import (
    get_analyst_agent,
    get_architect_agent,
    get_audit_service,
    get_current_user_claims,
    get_documentation_agent,
    get_optimizer_agent,
    get_planner_agent,
    get_research_agent,
    get_supervisor_agent,
    get_validator_agent,
)
from app.infrastructure.database.session import get_session
from app.infrastructure.llm.exceptions import GatewayError
from app.infrastructure.llm.message import ChatMessage, MessageRole
from app.infrastructure.llm.models import GatewayResponse
from app.infrastructure.repositories.research_conversation_repository import (
    SQLAlchemyResearchConversationRepository,
    generate_smart_title,
)
from app.infrastructure.repositories.research_execution_repository import (
    SQLAlchemyResearchExecutionRepository,
)
from app.schemas.agents import (
    AgentExecuteRequest,
    AgentInfoResponse,
    CreateConversationRequest,
    ResearchConversationDetailResponse,
    ResearchConversationResponse,
    ResearchExecutionItemResponse,
    ResearchMessageResponse,
    ResearchRunRequest,
    SendMessageRequest,
)
from app.schemas.response import SuccessResponse
from app.services.audit.audit_service import AuditService

logger = structlog.get_logger(__name__)

agents_router = APIRouter(prefix="/agents", tags=[AGENTS], responses=COMMON_RESPONSES)


@agents_router.get(
    "",
    response_model=SuccessResponse[list[AgentInfoResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Registered Agents",
    description="Fetch list of all 8 specialized registered AI agents in TWIB.",
)
async def list_agents() -> SuccessResponse[list[AgentInfoResponse]]:
    """Return all registered specialized AI agents."""
    agents_list = [
        AgentInfoResponse(
            id="planner",
            name="PlannerAgent",
            type="planner",
            role="Planning & Task Decomposition",
            description="Decomposes complex human requests into structured, actionable execution plans.",
            capabilities=["Task Decomposition", "Dependency Mapping", "Execution Strategy"],
        ),
        AgentInfoResponse(
            id="research",
            name="ResearchAgent",
            type="research",
            role="Intelligence & Data Gathering",
            description="Gathers external documentation, API references, and domain knowledge.",
            capabilities=["Web Search", "API Scraping", "Knowledge Retrieval"],
        ),
        AgentInfoResponse(
            id="analyst",
            name="AnalystAgent",
            type="analyst",
            role="Data & Requirements Analysis",
            description="Analyzes numerical data, system requirements, and constraint trade-offs.",
            capabilities=["Constraint Evaluation", "Metric Sizing", "Trade-Off Analysis"],
        ),
        AgentInfoResponse(
            id="architect",
            name="ArchitectAgent",
            type="architect",
            role="Software Architecture Design",
            description="Designs system architecture, component contracts, and database schemas.",
            capabilities=["System Design", "API Contract Spec", "Database Modeling"],
        ),
        AgentInfoResponse(
            id="validator",
            name="ValidatorAgent",
            type="validator",
            role="Validation & Testing",
            description="Validates code design, security policies, and test suite compliance.",
            capabilities=["OWASP Security Audit", "Contract Validation", "Edge-case Testing"],
        ),
        AgentInfoResponse(
            id="optimizer",
            name="OptimizerAgent",
            type="optimizer",
            role="Performance & Refactoring",
            description="Optimizes execution efficiency, latency bottlenecks, and code refactoring.",
            capabilities=["Performance Tuning", "Latency Reduction", "Code Refactoring"],
        ),
        AgentInfoResponse(
            id="documentation",
            name="DocumentationAgent",
            type="documentation",
            role="Documentation & Artifacts",
            description="Generates comprehensive markdown documentation, walkthroughs, and OpenAPI specs.",
            capabilities=["Markdown Generation", "API Spec Authoring", "Walkthrough Docs"],
        ),
        AgentInfoResponse(
            id="supervisor",
            name="SupervisorAgent",
            type="supervisor",
            role="Pipeline Orchestration",
            description="Orchestrates multi-agent pipelines, manages state, and monitors execution.",
            capabilities=["Pipeline Control", "State Transition", "Error Recovery"],
        ),
    ]
    return SuccessResponse[list[AgentInfoResponse]](data=agents_list)


def _parse_user_id(claims: dict[str, Any]) -> str | None:
    """Safely extract valid UUID user_id string from JWT claims."""
    sub = claims.get("sub")
    if not sub:
        return None
    try:
        uuid.UUID(str(sub))
        return str(sub)
    except ValueError:
        return None


async def _execute_agent_helper(
    agent: BaseAgent,
    agent_id: str,
    body: AgentExecuteRequest,
    audit_service: AuditService,
    claims: dict[str, Any],
) -> AgentResponse:
    """Helper for executing an agent instance with audit logging."""
    user_id = _parse_user_id(claims)
    await audit_service.record(
        action="agent.execution.started",
        resource_type="agent",
        resource_id=agent_id,
        user_id=user_id,
        metadata={"agent_type": agent_id},
    )

    request = AgentRequest(
        agent_id=agent_id,
        user_prompt=body.user_prompt,
        context=body.context,
        model=body.model,
        provider=body.provider,
        temperature=body.temperature,
        max_tokens=body.max_tokens,
    )

    try:
        response = await agent.execute(request)
        await audit_service.record(
            action="agent.execution.completed",
            resource_type="agent",
            resource_id=agent_id,
            user_id=user_id,
            metadata={"agent_type": agent_id, "status": response.status},
        )
        return response
    except AgentValidationError as err:
        await audit_service.record(
            action="agent.execution.failed",
            resource_type="agent",
            resource_id=agent_id,
            user_id=user_id,
            metadata={"agent_type": agent_id, "error": str(err)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except (AgentExecutionError, AgentError) as err:
        await audit_service.record(
            action="agent.execution.failed",
            resource_type="agent",
            resource_id=agent_id,
            user_id=user_id,
            metadata={"agent_type": agent_id, "error": str(err)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err),
        ) from err


# ------------------------------------------------------------------
# Persistent Research Conversations Endpoints
# ------------------------------------------------------------------

@agents_router.get(
    "/research/conversations",
    response_model=SuccessResponse[list[ResearchConversationResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Research Conversations",
    description="Fetch list of persistent research conversations for the user.",
)
async def list_research_conversations(
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session),
    limit: int = 50,
    offset: int = 0,
) -> SuccessResponse[list[ResearchConversationResponse]]:
    user_id_str = _parse_user_id(claims)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid user identity required.",
        )

    repo = SQLAlchemyResearchConversationRepository(session)
    conversations = await repo.list_conversations_by_user(
        uuid.UUID(user_id_str),
        limit=limit,
        offset=offset,
    )

    items = []
    for conv in conversations:
        snippet = conv.messages[-1].content[:100] if conv.messages else None
        items.append(
            ResearchConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                title=conv.title,
                agent_type=conv.agent_type,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                last_message_snippet=snippet,
            )
        )
    return SuccessResponse[list[ResearchConversationResponse]](data=items)


@agents_router.post(
    "/research/conversations",
    response_model=SuccessResponse[ResearchConversationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Research Conversation",
    description="Create a new empty persistent research conversation thread.",
)
async def create_research_conversation(
    body: CreateConversationRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse[ResearchConversationResponse]:
    user_id_str = _parse_user_id(claims)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid user identity required.",
        )

    repo = SQLAlchemyResearchConversationRepository(session)
    conv = await repo.create_conversation(
        user_id=uuid.UUID(user_id_str),
        title=body.title or "New Research",
        agent_type=body.agent_type or "research",
    )
    await session.commit()

    return SuccessResponse[ResearchConversationResponse](
        data=ResearchConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            agent_type=conv.agent_type,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            last_message_snippet=None,
        )
    )


@agents_router.get(
    "/research/conversations/{conversation_id}",
    response_model=SuccessResponse[ResearchConversationDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Research Conversation Details",
    description="Retrieve a conversation and all its message turns by ID.",
)
async def get_research_conversation(
    conversation_id: uuid.UUID,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse[ResearchConversationDetailResponse]:
    user_id_str = _parse_user_id(claims)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid user identity required.",
        )

    repo = SQLAlchemyResearchConversationRepository(session)
    conv = await repo.get_conversation(conversation_id, uuid.UUID(user_id_str))
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied.",
        )

    msg_responses = [
        ResearchMessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            metadata=msg.metadata_json or {},
            created_at=msg.created_at,
        )
        for msg in conv.messages
    ]

    return SuccessResponse[ResearchConversationDetailResponse](
        data=ResearchConversationDetailResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            agent_type=conv.agent_type,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=msg_responses,
        )
    )


@agents_router.post(
    "/research/conversations/{conversation_id}/messages",
    response_model=SuccessResponse[ResearchMessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Send Message in Research Conversation",
    description="Post user prompt to conversation, run OmniRoute LLM with history.",
)
async def send_research_conversation_message(
    conversation_id: str,
    body: SendMessageRequest,
    agent: ResearchAgent = Depends(get_research_agent),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse[ResearchMessageResponse]:
    user_id_str = _parse_user_id(claims)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid user identity required.",
        )

    user_uuid = uuid.UUID(user_id_str)
    repo = SQLAlchemyResearchConversationRepository(session)

    # 1. Resolve or create conversation
    conv = None
    if conversation_id != "new":
        try:
            conv_uuid = uuid.UUID(conversation_id)
            conv = await repo.get_conversation(conv_uuid, user_uuid)
        except ValueError:
            pass

    if not conv:
        smart_title = generate_smart_title(body.prompt)
        conv = await repo.create_conversation(
            user_id=user_uuid,
            title=smart_title,
            agent_type="research",
        )

    # 2. Add user message
    await repo.add_message(
        conversation_id=conv.id,
        role="user",
        content=body.prompt.strip(),
    )

    conv = await repo.get_conversation(conv.id, user_uuid)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load updated conversation.",
        )

    if len(conv.messages) <= 2 or conv.title == "New Research":
        smart_title = generate_smart_title(body.prompt)
        await repo.update_title(conv.id, user_uuid, smart_title)

    # 3. Construct chat message history for OmniRoute Gateway
    chat_messages: list[ChatMessage] = []
    for msg in conv.messages:
        role_enum = MessageRole.USER if msg.role == "user" else MessageRole.ASSISTANT
        chat_messages.append(ChatMessage(role=role_enum, content=msg.content))

    if len(chat_messages) > 10:
        chat_messages = chat_messages[-10:]

    # 4. Call ResearchAgent with full conversation history
    try:
        gw_res = await agent.run_conversation(
            chat_messages,
            temperature=body.temperature,
            model=body.model,
        )

        # 5. Persist assistant response
        assistant_meta = {
            "provider": gw_res.provider,
            "model": gw_res.model,
            "latency_ms": gw_res.latency_ms,
            "usage": gw_res.usage.model_dump(),
        }
        assistant_msg = await repo.add_message(
            conversation_id=conv.id,
            role="assistant",
            content=gw_res.answer,
            metadata_json=assistant_meta,
        )

        await session.commit()

        return SuccessResponse[ResearchMessageResponse](
            data=ResearchMessageResponse(
                id=assistant_msg.id,
                conversation_id=assistant_msg.conversation_id,
                role=assistant_msg.role,
                content=assistant_msg.content,
                metadata=assistant_msg.metadata_json,
                created_at=assistant_msg.created_at,
            )
        )
    except GatewayError as err:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OmniRoute service is currently unavailable. Please try again.",
        ) from err
    except Exception as err:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err),
        ) from err


@agents_router.delete(
    "/research/conversations/{conversation_id}",
    response_model=SuccessResponse[dict[str, bool]],
    status_code=status.HTTP_200_OK,
    summary="Delete Research Conversation",
    description="Delete a conversation and all its messages.",
)
async def delete_research_conversation(
    conversation_id: uuid.UUID,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse[dict[str, bool]]:
    user_id_str = _parse_user_id(claims)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid user identity required.",
        )

    repo = SQLAlchemyResearchConversationRepository(session)
    deleted = await repo.delete_conversation(conversation_id, uuid.UUID(user_id_str))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied.",
        )

    await session.commit()
    return SuccessResponse[dict[str, bool]](data={"deleted": True})


# ------------------------------------------------------------------
# Legacy & Synchronous Execution Endpoints
# ------------------------------------------------------------------

@agents_router.post(
    "/research/run",
    response_model=SuccessResponse[GatewayResponse],
    status_code=status.HTTP_200_OK,
    summary="Run Research Agent via Gateway",
    description=(
        "Run ResearchAgent synchronously backed by OmniRoute / LLMGateway. "
        "Returns TWIB-specific answer, provider, model, latency_ms, and usage."
    ),
)
async def run_research(
    body: ResearchRunRequest,
    agent: ResearchAgent = Depends(get_research_agent),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session),
) -> SuccessResponse[GatewayResponse]:
    """Execute synchronous prompt -> response ResearchAgent run and store execution."""
    user_id_str = _parse_user_id(claims)
    await audit_service.record(
        action="agent.research.run_started",
        resource_type="agent",
        resource_id="researcher",
        user_id=user_id_str,
        metadata={"model": body.model, "temperature": body.temperature},
    )

    try:
        gateway_res = await agent.run(
            prompt=body.prompt,
            temperature=body.temperature,
            model=body.model,
        )

        # Store execution entity if valid user_id present
        if user_id_str:
            try:
                repo = SQLAlchemyResearchExecutionRepository(session)
                await repo.create(
                    user_id=uuid.UUID(user_id_str),
                    prompt=body.prompt,
                    response=gateway_res.answer,
                    provider=gateway_res.provider,
                    model=gateway_res.model,
                    latency_ms=gateway_res.latency_ms,
                    usage=gateway_res.usage.model_dump(),
                )
                await session.commit()
            except Exception as store_err:
                logger.warning(
                    "Failed to persist research execution entity",
                    error=str(store_err),
                )

        await audit_service.record(
            action="agent.research.run_completed",
            resource_type="agent",
            resource_id="researcher",
            user_id=user_id_str,
            metadata={
                "provider": gateway_res.provider,
                "model": gateway_res.model,
                "latency_ms": gateway_res.latency_ms,
            },
        )
        return SuccessResponse[GatewayResponse](data=gateway_res)
    except AgentValidationError as err:
        await audit_service.record(
            action="agent.research.run_failed",
            resource_type="agent",
            resource_id="researcher",
            user_id=user_id_str,
            metadata={"error": str(err)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except GatewayError as err:
        await audit_service.record(
            action="agent.research.run_failed",
            resource_type="agent",
            resource_id="researcher",
            user_id=user_id_str,
            metadata={"error": str(err)},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM Gateway unavailable: {err}",
        ) from err
    except (AgentExecutionError, AgentError) as err:
        await audit_service.record(
            action="agent.research.run_failed",
            resource_type="agent",
            resource_id="researcher",
            user_id=user_id_str,
            metadata={"error": str(err)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(err),
        ) from err


@agents_router.get(
    "/research/history",
    response_model=SuccessResponse[list[ResearchExecutionItemResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get Research Execution History",
    description="Fetch latest ResearchAgent execution history for current user.",
)
async def get_research_history(
    claims: dict[str, Any] = Depends(get_current_user_claims),
    session: AsyncSession = Depends(get_session),
    limit: int = 50,
    offset: int = 0,
) -> SuccessResponse[list[ResearchExecutionItemResponse]]:
    """Retrieve research execution records for current authenticated user."""
    user_id_str = _parse_user_id(claims)
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid user identity sub claim required.",
        )

    repo = SQLAlchemyResearchExecutionRepository(session)
    records = await repo.list_by_user(
        uuid.UUID(user_id_str),
        limit=limit,
        offset=offset,
    )

    data_items = [
        ResearchExecutionItemResponse(
            id=rec.id,
            user_id=rec.user_id,
            prompt=rec.prompt,
            response=rec.response,
            provider=rec.provider,
            model=rec.model,
            latency_ms=rec.latency_ms,
            usage=rec.usage,
            created_at=rec.created_at,
        )
        for rec in records
    ]
    return SuccessResponse[list[ResearchExecutionItemResponse]](data=data_items)


@agents_router.post(
    "/planner/execute",
    response_model=AgentResponse,
    summary="Execute Planner Agent",
)
async def execute_planner(
    body: AgentExecuteRequest,
    agent: PlannerAgent = Depends(get_planner_agent),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> AgentResponse:
    """Decompose human objective into structured tasks."""
    return await _execute_agent_helper(agent, "planner", body, audit_service, claims)


@agents_router.post(
    "/research/execute",
    response_model=AgentResponse,
    summary="Execute Research Agent",
)
async def execute_research(
    body: AgentExecuteRequest,
    agent: ResearchAgent = Depends(get_research_agent),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> AgentResponse:
    """Gather knowledge and conduct context research."""
    return await _execute_agent_helper(agent, "research", body, audit_service, claims)


@agents_router.post(
    "/analyst/execute",
    response_model=AgentResponse,
    summary="Execute Analyst Agent",
)
async def execute_analyst(
    body: AgentExecuteRequest,
    agent: AnalystAgent = Depends(get_analyst_agent),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> AgentResponse:
    """Synthesize requirements and extract functional specifications."""
    return await _execute_agent_helper(agent, "analyst", body, audit_service, claims)


@agents_router.post(
    "/architect/execute",
    response_model=AgentResponse,
    summary="Execute Architect Agent",
)
async def execute_architect(
    body: AgentExecuteRequest,
    agent: ArchitectAgent = Depends(get_architect_agent),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> AgentResponse:
    """Design system architecture and component specifications."""
    return await _execute_agent_helper(agent, "architect", body, audit_service, claims)


@agents_router.post(
    "/validator/execute",
    response_model=AgentResponse,
    summary="Execute Validator Agent",
)
async def execute_validator(
    body: AgentExecuteRequest,
    agent: ValidatorAgent = Depends(get_validator_agent),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> AgentResponse:
    """Validate specifications and check compliance rules."""
    return await _execute_agent_helper(agent, "validator", body, audit_service, claims)


@agents_router.post(
    "/optimizer/execute",
    response_model=AgentResponse,
    summary="Execute Optimizer Agent",
)
async def execute_optimizer(
    body: AgentExecuteRequest,
    agent: OptimizerAgent = Depends(get_optimizer_agent),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> AgentResponse:
    """Optimize architecture and improve performance profiles."""
    return await _execute_agent_helper(agent, "optimizer", body, audit_service, claims)


@agents_router.post(
    "/documentation/execute",
    response_model=AgentResponse,
    summary="Execute Documentation Agent",
)
async def execute_documentation(
    body: AgentExecuteRequest,
    agent: DocumentationAgent = Depends(get_documentation_agent),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> AgentResponse:
    """Generate technical documentation and walkthrough artifacts."""
    return await _execute_agent_helper(
        agent, "documentation", body, audit_service, claims
    )


@agents_router.post(
    "/supervisor/execute",
    response_model=AgentResponse,
    summary="Execute Supervisor Agent",
)
async def execute_supervisor(
    body: AgentExecuteRequest,
    agent: SupervisorAgent = Depends(get_supervisor_agent),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> AgentResponse:
    """Orchestrate multi-agent workflow pipelines."""
    return await _execute_agent_helper(agent, "supervisor", body, audit_service, claims)


@agents_router.post(
    "/plan-dag",
    response_model=AgentDAGPlan,
    summary="Plan Dynamic Multi-Agent DAG",
    description="Generate an adaptive Directed Acyclic Graph (DAG) plan for multi-agent workflow execution.",
)
async def plan_dag(
    body: AgentExecuteRequest,
    agent: SupervisorAgent = Depends(get_supervisor_agent),
) -> AgentDAGPlan:
    """Plan an adaptive DAG for multi-agent orchestration."""
    try:
        return await agent.plan_dag(
            goal=body.user_prompt,
            context=body.context,
            provider=body.provider,
            model=body.model,
        )
    except AgentValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(err), "agent_id": "supervisor"},
        ) from err
    except Exception as err:
        logger.error("DAG planning failed: %s", err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DAG planning failed: {err}",
        ) from err


@agents_router.post(
    "/supervisor/dag",
    response_model=AgentResponse,
    summary="Execute Dynamic Multi-Agent DAG",
    description="Execute a dynamic DAG multi-agent workflow with concurrent topological dispatch.",
)
async def execute_supervisor_dag(
    body: AgentExecuteRequest,
    agent: SupervisorAgent = Depends(get_supervisor_agent),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> AgentResponse:
    """Execute dynamic DAG multi-agent pipeline."""
    # Force dynamic routing flag in context
    ctx = dict(body.context or {})
    ctx["dynamic_routing"] = True
    body.context = ctx
    return await _execute_agent_helper(agent, "supervisor", body, audit_service, claims)

