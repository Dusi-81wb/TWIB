"""Audit Log v1 API endpoints.

Exposes endpoints for querying and filtering security audit logs:
- ``GET /api/v1/audit``: Retrieve filtered security audit log entries.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, status

from app.api.tags import AUDIT
from app.authorization.decorators import RequireOrganizationRole
from app.authorization.roles import UserRole
from app.dependencies import get_audit_service
from app.schemas.audit import AuditLogListResponse, AuditLogResponse
from app.services.audit import AuditService

audit_router = APIRouter(prefix="/audit", tags=[AUDIT])


@audit_router.get(
    "",
    response_model=AuditLogListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Audit Logs",
    description=(
        "Retrieve security audit logs filtered by organization, workspace, "
        "user, action, and date range. Requires Organization Admin or Owner role."
    ),
    dependencies=[Depends(RequireOrganizationRole(UserRole.ADMIN))],
    responses={
        200: {
            "description": "Filtered list of security audit logs.",
        },
        403: {
            "description": "Forbidden: Requires Organization Admin or Owner role.",
        },
    },
)
async def get_audit_logs(
    org_id: str | None = Query(
        default=None,
        description="Optional Organization UUID filter.",
    ),
    workspace_id: str | None = Query(
        default=None,
        description="Optional Workspace UUID filter.",
    ),
    user_id: str | None = Query(
        default=None,
        description="Optional actor User UUID filter.",
    ),
    action: str | None = Query(
        default=None,
        description="Optional action filter (e.g. 'user.login').",
    ),
    start_date: str | None = Query(
        default=None,
        description="Optional ISO 8601 start timestamp filter.",
    ),
    end_date: str | None = Query(
        default=None,
        description="Optional ISO 8601 end timestamp filter.",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
        description="Maximum items per page.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Page offset index.",
    ),
    audit_service: AuditService = Depends(get_audit_service),
) -> Any:
    """Retrieve filtered audit logs.

    Args:
        org_id: Optional Organization UUID string.
        workspace_id: Optional Workspace UUID string.
        user_id: Optional User UUID string.
        action: Optional action filter string.
        start_date: Optional ISO start timestamp.
        end_date: Optional ISO end timestamp.
        limit: Items per page (default 50).
        offset: Offset index (default 0).
        audit_service: Injected AuditService instance.

    Returns:
        AuditLogListResponse containing paginated audit items and total count.
    """
    logs, total = await audit_service.get_logs(
        organization_id=org_id,
        workspace_id=workspace_id,
        user_id=user_id,
        action=action,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )

    items = [
        AuditLogResponse(
            id=str(log.id.value),
            organization_id=str(log.organization_id.value)
            if log.organization_id
            else None,
            workspace_id=str(log.workspace_id.value)
            if log.workspace_id
            else None,
            user_id=str(log.user_id.value) if log.user_id else None,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            timestamp=log.timestamp.value.isoformat(),
            metadata=log.metadata,
        )
        for log in logs
    ]

    return AuditLogListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )
