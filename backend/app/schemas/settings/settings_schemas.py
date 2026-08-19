"""Settings and Onboarding Schema Definitions."""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class OnboardingStatusResponse(BaseModel):
    """Status of user/system onboarding and initial configuration."""

    onboarding_completed: bool = Field(..., description="Whether setup has been completed.")
    workspace_configured: bool = Field(..., description="Whether at least one workspace exists.")
    omniroute_configured: bool = Field(..., description="Whether OmniRoute API key is configured.")
    default_model: str = Field(default="best-free", description="Default model routing strategy.")
    workspace_name: str | None = Field(default=None, description="Name of the initial workspace if created.")
    services_health: dict[str, Any] = Field(default_factory=dict, description="Live connectivity health map.")


class OnboardingCompleteRequest(BaseModel):
    """Payload to complete the initial TWIB setup wizard."""

    workspace_name: str = Field(..., min_length=2, max_length=100, description="Workspace display name.")
    workspace_purpose: str | None = Field(default=None, max_length=100, description="Workspace use case / purpose.")
    workspace_description: str | None = Field(default=None, max_length=500, description="Optional workspace description.")
    omniroute_api_key: str = Field(..., min_length=3, description="OmniRoute Gateway API key.")
    omniroute_base_url: str | None = Field(default="http://localhost:8080/v1", description="OmniRoute Gateway base URL.")
    default_model: str | None = Field(default="best-free", description="Default selected model/router.")


class OmniRouteTestRequest(BaseModel):
    """Request payload to test connection with OmniRoute gateway."""

    api_key: str = Field(..., min_length=3, description="API Key to test.")
    base_url: str | None = Field(default="http://localhost:8080/v1", description="OmniRoute base URL.")
    model: str | None = Field(default="best-free", description="Target model for test completion.")


class OmniRouteTestResponse(BaseModel):
    """Response payload resulting from OmniRoute connection test."""

    success: bool = Field(..., description="Whether gateway test succeeded.")
    latency_ms: float = Field(default=0.0, description="Measured response latency in milliseconds.")
    message: str = Field(..., description="Status explanation or error details.")
    available_models: list[str] = Field(default_factory=list, description="List of available models returned by gateway.")


class OmniRouteConfigResponse(BaseModel):
    """Current OmniRoute gateway configuration state."""

    base_url: str = Field(..., description="Base URL of OmniRoute.")
    default_model: str = Field(..., description="Default model routing strategy.")
    is_configured: bool = Field(..., description="Whether an API key is set.")
    masked_api_key: str = Field(..., description="Masked API key representation.")


class OmniRouteUpdateRequest(BaseModel):
    """Payload to update OmniRoute gateway configuration."""

    omniroute_api_key: str | None = Field(default=None, description="New OmniRoute API key.")
    omniroute_base_url: str | None = Field(default=None, description="New OmniRoute base URL.")
    default_model: str | None = Field(default=None, description="New default model identifier.")


class DashboardMetricsResponse(BaseModel):
    """Live aggregated dashboard metrics with zero placeholder data."""

    total_workflows: int = Field(default=0, description="Total workflows registered.")
    active_workflows: int = Field(default=0, description="Number of currently executing workflows.")
    completed_workflows: int = Field(default=0, description="Number of successfully completed workflows.")
    failed_workflows: int = Field(default=0, description="Number of failed workflows.")
    total_workspaces: int = Field(default=0, description="Number of workspaces for user.")
    total_organizations: int = Field(default=0, description="Number of organizations.")
    total_agents: int = Field(default=8, description="Number of registered autonomous agents.")
    recent_executions: list[dict[str, Any]] = Field(default_factory=list, description="Recent execution history.")
    recent_workflows: list[dict[str, Any]] = Field(default_factory=list, description="Recent workflows list.")
    services_status: dict[str, Any] = Field(default_factory=dict, description="Live status of underlying services.")
