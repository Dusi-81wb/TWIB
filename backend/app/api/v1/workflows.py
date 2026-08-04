"""Workflow REST API router for v1 endpoints.

Exposes REST API endpoints for workflow creation, execution, control, history tracking,
and template instantiation:

- ``POST /api/v1/workflows``: Create a workflow.
- ``GET /api/v1/workflows``: List registered workflows.
- ``GET /api/v1/workflows/templates``: List templates.
- ``POST /api/v1/workflows/templates/{id}/instantiate``: Instantiate template.
- ``GET /api/v1/workflows/{id}``: Get workflow details.
- ``POST /api/v1/workflows/{id}/start``: Start execution.
- ``POST /api/v1/workflows/{id}/pause``: Pause execution.
- ``POST /api/v1/workflows/{id}/resume``: Resume execution.
- ``POST /api/v1/workflows/{id}/cancel``: Cancel workflow.
- ``GET /api/v1/workflows/{id}/history``: Get workflow state history.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.openapi import COMMON_RESPONSES
from app.api.tags import WORKFLOWS
from app.dependencies import (
    get_audit_service,
    get_current_user_claims,
    get_workflow_engine,
    get_workflow_executor,
    get_workflow_state_manager,
    get_workflow_template_service,
)
from app.schemas.workflows import (
    CreateWorkflowRequest,
    InstantiateTemplateRequest,
    StateHistoryEntryResponse,
    StateHistoryResponse,
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowStepResponse,
    WorkflowTemplateListResponse,
    WorkflowTemplateResponse,
)
from app.services.audit.audit_service import AuditService
from app.workflows.workflow import Workflow
from app.workflows.workflow_engine import WorkflowEngine
from app.workflows.workflow_exceptions import (
    WorkflowExecutionError,
    WorkflowNotFoundError,
    WorkflowStateError,
    WorkflowValidationError,
)
from app.workflows.workflow_executor import WorkflowExecutor
from app.workflows.workflow_models import WorkflowStep
from app.workflows.workflow_state import StateHistoryEntry
from app.workflows.workflow_state_manager import WorkflowStateManager
from app.workflows.workflow_template import WorkflowTemplate
from app.workflows.workflow_template_service import WorkflowTemplateService

workflows_router = APIRouter(
    prefix="/workflows", tags=[WORKFLOWS], responses=COMMON_RESPONSES
)


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


def _workflow_to_response(wf: Workflow) -> WorkflowResponse:
    """Convert Workflow domain entity to WorkflowResponse schema."""
    step_responses = [
        WorkflowStepResponse(
            step_id=s.step_id,
            name=s.name,
            agent_id=s.agent_id,
            status=s.status.value if hasattr(s.status, "value") else str(s.status),
            input_data=s.input_data,
            output_data=s.output_data,
            error=s.error,
            started_at=s.started_at.isoformat() if s.started_at else None,
            completed_at=s.completed_at.isoformat() if s.completed_at else None,
        )
        for s in wf.execution_steps
    ]
    return WorkflowResponse(
        workflow_id=wf.workflow_id,
        workflow_name=wf.workflow_name,
        user_request=wf.user_request,
        workflow_status=wf.workflow_status.value
        if hasattr(wf.workflow_status, "value")
        else str(wf.workflow_status),
        created_at=wf.created_at.isoformat(),
        updated_at=wf.updated_at.isoformat(),
        execution_steps=step_responses,
        metadata=wf.metadata,
    )


def _template_to_response(tpl: WorkflowTemplate) -> WorkflowTemplateResponse:
    """Convert WorkflowTemplate domain entity to WorkflowTemplateResponse schema."""
    return WorkflowTemplateResponse(
        template_id=tpl.template_id,
        template_name=tpl.template_name,
        description=tpl.description,
        category=tpl.category.value
        if hasattr(tpl.category, "value")
        else str(tpl.category),
        workflow_definition=tpl.workflow_definition,
        default_configuration=tpl.default_configuration,
        supported_agents=tpl.supported_agents,
        requires_approval=tpl.requires_approval,
        version=tpl.version,
    )


def _history_to_response(
    history: list[StateHistoryEntry], workflow_id: str
) -> StateHistoryResponse:
    """Convert StateHistoryEntry list to StateHistoryResponse schema."""
    entries = [
        StateHistoryEntryResponse(
            previous_state=e.previous_state.value
            if e.previous_state and hasattr(e.previous_state, "value")
            else (str(e.previous_state) if e.previous_state else None),
            current_state=e.current_state.value
            if hasattr(e.current_state, "value")
            else str(e.current_state),
            timestamp=e.timestamp.isoformat(),
            triggering_event=e.triggering_event,
            metadata=e.metadata,
        )
        for e in history
    ]
    return StateHistoryResponse(workflow_id=workflow_id, history=entries)


@workflows_router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a workflow",
)
async def create_workflow(
    body: CreateWorkflowRequest,
    engine: WorkflowEngine = Depends(get_workflow_engine),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> WorkflowResponse:
    """Create a new Workflow instance."""
    try:
        raw_steps = body.steps or []
        steps = [
            WorkflowStep(
                name=s.get("name", "Custom Step"),
                agent_id=s.get("agent_id"),
                input_data=s.get("input_data", {}),
            )
            for s in raw_steps
        ]
        wf = engine.create_workflow(
            workflow_name=body.workflow_name,
            user_request=body.user_request,
            steps=steps if steps else None,
            metadata=body.metadata,
        )
        await audit_service.record(
            action="workflow.created",
            resource_type="workflow",
            resource_id=wf.workflow_id,
            user_id=_parse_user_id(claims),
        )
        return _workflow_to_response(wf)
    except WorkflowValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err


@workflows_router.get(
    "",
    response_model=WorkflowListResponse,
    summary="List workflows",
)
async def list_workflows(
    engine: WorkflowEngine = Depends(get_workflow_engine),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> WorkflowListResponse:
    """List registered workflow instances."""
    all_workflows = list(engine._workflows.values())
    return WorkflowListResponse(
        items=[_workflow_to_response(w) for w in all_workflows],
        total=len(all_workflows),
    )


@workflows_router.get(
    "/templates",
    response_model=WorkflowTemplateListResponse,
    summary="List workflow templates",
)
async def list_templates(
    category: str | None = Query(default=None, description="Optional category filter"),
    template_service: WorkflowTemplateService = Depends(get_workflow_template_service),
) -> WorkflowTemplateListResponse:
    """List available workflow templates."""
    templates = template_service.list_templates(category=category)
    return WorkflowTemplateListResponse(
        items=[_template_to_response(t) for t in templates],
        total=len(templates),
    )


@workflows_router.post(
    "/templates/{template_id}/instantiate",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Instantiate template into a workflow",
)
async def instantiate_template(
    template_id: str,
    body: InstantiateTemplateRequest,
    template_service: WorkflowTemplateService = Depends(get_workflow_template_service),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> WorkflowResponse:
    """Instantiate a new runnable Workflow from a template blueprint."""
    try:
        wf = template_service.instantiate_workflow(
            template_id=template_id,
            user_request=body.user_request,
            custom_name=body.custom_name,
            configuration_overrides=body.configuration_overrides,
        )
        await audit_service.record(
            action="workflow.instantiated_from_template",
            resource_type="workflow",
            resource_id=wf.workflow_id,
            user_id=_parse_user_id(claims),
            metadata={"template_id": template_id},
        )
        return _workflow_to_response(wf)
    except WorkflowNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
    except WorkflowValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err


@workflows_router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Get workflow details",
)
async def get_workflow(
    workflow_id: str,
    engine: WorkflowEngine = Depends(get_workflow_engine),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> WorkflowResponse:
    """Retrieve details for a specific workflow."""
    try:
        wf = engine.load_workflow(workflow_id)
        return _workflow_to_response(wf)
    except WorkflowNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err


@workflows_router.post(
    "/{workflow_id}/start",
    response_model=WorkflowResponse,
    summary="Start workflow execution",
)
async def start_workflow(
    workflow_id: str,
    executor: WorkflowExecutor = Depends(get_workflow_executor),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> WorkflowResponse:
    """Start execution of a registered workflow."""
    try:
        wf = await executor.execute(workflow_id)
        await audit_service.record(
            action="workflow.started",
            resource_type="workflow",
            resource_id=workflow_id,
            user_id=_parse_user_id(claims),
        )
        return _workflow_to_response(wf)
    except WorkflowNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
    except (WorkflowValidationError, WorkflowStateError) as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err
    except WorkflowExecutionError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err


@workflows_router.post(
    "/{workflow_id}/pause",
    response_model=WorkflowResponse,
    summary="Pause workflow execution",
)
async def pause_workflow(
    workflow_id: str,
    executor: WorkflowExecutor = Depends(get_workflow_executor),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> WorkflowResponse:
    """Pause an in-flight workflow execution."""
    try:
        wf = executor.pause_execution(workflow_id)
        await audit_service.record(
            action="workflow.paused",
            resource_type="workflow",
            resource_id=workflow_id,
            user_id=_parse_user_id(claims),
        )
        return _workflow_to_response(wf)
    except WorkflowNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
    except WorkflowStateError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err


@workflows_router.post(
    "/{workflow_id}/resume",
    response_model=WorkflowResponse,
    summary="Resume workflow execution",
)
async def resume_workflow(
    workflow_id: str,
    executor: WorkflowExecutor = Depends(get_workflow_executor),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> WorkflowResponse:
    """Resume execution of a paused workflow."""
    try:
        wf = await executor.resume_execution(workflow_id)
        await audit_service.record(
            action="workflow.resumed",
            resource_type="workflow",
            resource_id=workflow_id,
            user_id=_parse_user_id(claims),
        )
        return _workflow_to_response(wf)
    except WorkflowNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
    except (WorkflowValidationError, WorkflowStateError) as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err
    except WorkflowExecutionError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
        ) from err


@workflows_router.post(
    "/{workflow_id}/cancel",
    response_model=WorkflowResponse,
    summary="Cancel workflow execution",
)
async def cancel_workflow(
    workflow_id: str,
    executor: WorkflowExecutor = Depends(get_workflow_executor),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> WorkflowResponse:
    """Cancel execution of a registered workflow."""
    try:
        wf = executor.stop_execution(workflow_id)
        await audit_service.record(
            action="workflow.cancelled",
            resource_type="workflow",
            resource_id=workflow_id,
            user_id=_parse_user_id(claims),
        )
        return _workflow_to_response(wf)
    except WorkflowNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
    except WorkflowStateError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err


@workflows_router.get(
    "/{workflow_id}/history",
    response_model=StateHistoryResponse,
    summary="Get workflow state history",
)
async def get_workflow_history(
    workflow_id: str,
    state_manager: WorkflowStateManager = Depends(get_workflow_state_manager),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> StateHistoryResponse:
    """Retrieve full state transition history for a workflow."""
    try:
        history = state_manager.get_history(workflow_id)
        return _history_to_response(history, workflow_id)
    except WorkflowNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err
