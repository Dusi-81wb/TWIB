"""Monitoring REST API router for v1 endpoints.

Exposes REST API endpoints for runtime system health, workflow execution metrics,
agent performance telemetry, and detailed workflow diagnostics:

- ``GET /api/v1/monitoring/health``: System health status overview.
- ``GET /api/v1/monitoring/workflows``: Aggregated workflow metrics summary.
- ``GET /api/v1/monitoring/workflows/{id}``: Individual workflow diagnostic snapshot.
- ``GET /api/v1/monitoring/agents``: Aggregated agent execution metrics.
- ``GET /api/v1/monitoring/system``: Detailed subsystem component health.
- ``GET /api/v1/monitoring/metrics``: Unified monitoring and telemetry report.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.openapi import COMMON_RESPONSES
from app.api.tags import MONITORING
from app.dependencies import (
    get_audit_service,
    get_current_user_claims,
    get_monitoring_service,
)
from app.schemas.monitoring import (
    AgentMetricsSummary,
    SystemHealthReport,
    UnifiedMetricsReport,
    WorkflowMetricsSummary,
    WorkflowMonitoringDetails,
)
from app.services.audit.audit_service import AuditService
from app.services.monitoring_service import MonitoringService
from app.workflows.workflow_exceptions import WorkflowNotFoundError

monitoring_router = APIRouter(
    prefix="/monitoring", tags=[MONITORING], responses=COMMON_RESPONSES
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


@monitoring_router.get(
    "/health",
    response_model=SystemHealthReport,
    summary="Get system health status",
)
async def get_health_status(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> SystemHealthReport:
    """Retrieve health status overview across all backend subsystems."""
    return await monitoring_service.get_system_health()


@monitoring_router.get(
    "/workflows",
    response_model=WorkflowMetricsSummary,
    summary="Get workflow metrics summary",
)
async def get_workflow_metrics(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> WorkflowMetricsSummary:
    """Retrieve aggregated workflow metrics."""
    return monitoring_service.get_workflow_metrics()


@monitoring_router.get(
    "/workflows/{workflow_id}",
    response_model=WorkflowMonitoringDetails,
    summary="Get workflow diagnostic details",
)
async def get_workflow_diagnostic_details(
    workflow_id: str,
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    audit_service: AuditService = Depends(get_audit_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> WorkflowMonitoringDetails:
    """Retrieve detailed runtime diagnostics for a specific workflow."""
    try:
        details = monitoring_service.get_workflow_details(workflow_id)
        await audit_service.record(
            action="monitoring.workflow_inspected",
            resource_type="workflow",
            resource_id=workflow_id,
            user_id=_parse_user_id(claims),
        )
        return details
    except WorkflowNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@monitoring_router.get(
    "/agents",
    response_model=AgentMetricsSummary,
    summary="Get agent metrics summary",
)
async def get_agent_metrics(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> AgentMetricsSummary:
    """Retrieve aggregated execution metrics across all AI agents."""
    return monitoring_service.get_agent_metrics()


@monitoring_router.get(
    "/system",
    response_model=SystemHealthReport,
    summary="Get detailed system status",
)
async def get_detailed_system_status(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> SystemHealthReport:
    """Retrieve detailed health report for system components."""
    return await monitoring_service.get_system_health()


@monitoring_router.get(
    "/metrics",
    response_model=UnifiedMetricsReport,
    summary="Get unified metrics report",
)
async def get_unified_metrics_report(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> UnifiedMetricsReport:
    """Retrieve unified report combining health, workflow, and agent metrics."""
    return await monitoring_service.get_unified_metrics()
