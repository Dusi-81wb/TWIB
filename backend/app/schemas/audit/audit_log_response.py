"""Audit Log response Pydantic schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Response payload representing an individual audit log entry."""

    id: str = Field(..., description="Unique UUID identity of the audit log entry.")
    organization_id: str | None = Field(
        default=None,
        description="Organization UUID context.",
    )
    workspace_id: str | None = Field(
        default=None,
        description="Workspace UUID context.",
    )
    user_id: str | None = Field(
        default=None,
        description="Actor User UUID identity.",
    )
    action: str = Field(
        ...,
        description="Audited action string (e.g. 'user.login').",
    )
    resource_type: str = Field(
        ...,
        description="Affected resource type (e.g. 'user', 'api_key').",
    )
    resource_id: str | None = Field(
        default=None,
        description="Affected resource UUID or ID.",
    )
    ip_address: str = Field(default="", description="Client IP address.")
    user_agent: str = Field(default="", description="Client User-Agent string.")
    timestamp: str = Field(
        ...,
        description="UTC ISO 8601 timestamp string.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Sanitized audit metadata.",
    )


class AuditLogListResponse(BaseModel):
    """Paginated list response containing audit log entries."""

    items: list[AuditLogResponse] = Field(..., description="List of audit log items.")
    total: int = Field(..., description="Total matching audit log entries count.")
    limit: int = Field(..., description="Maximum items per page.")
    offset: int = Field(..., description="Page offset index.")
