"""Agent REST API router for v1 endpoints.

Exposes REST API endpoints for agent execution across all 8 specialized agents:

- ``POST /api/v1/agents/planner/execute``: Execute Planner Agent.
- ``POST /api/v1/agents/research/execute``: Execute Research Agent.
- ``POST /api/v1/agents/analyst/execute``: Execute Analyst Agent.
- ``POST /api/v1/agents/architect/execute``: Execute Architect Agent.
- ``POST /api/v1/agents/validator/execute``: Execute Validator Agent.
- ``POST /api/v1/agents/optimizer/execute``: Execute Optimizer Agent.
- ``POST /api/v1/agents/documentation/execute``: Execute Documentation Agent.
- ``POST /api/v1/agents/supervisor/execute``: Execute Supervisor Agent.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

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
from app.schemas.agents import AgentExecuteRequest
from app.services.audit.audit_service import AuditService

agents_router = APIRouter(prefix="/agents", tags=[AGENTS], responses=COMMON_RESPONSES)


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
    """Decompose user goal into a structured execution plan."""
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
    """Design high-level system architecture and component blueprints."""
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
    """Audit content quality, consistency, and structural integrity."""
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
    """Optimize output clarity, completeness, and structure."""
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
    """Format and generate professional technical documentation."""
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
    """Orchestrate multi-agent execution pipeline for objective."""
    return await _execute_agent_helper(agent, "supervisor", body, audit_service, claims)
