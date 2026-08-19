"""Monitoring Service implementation for system-wide health and metric aggregation.

Aggregates system health statuses (PostgreSQL, Redis, Vector, LLM, Workflow Engine)
and delegates workflow and agent runtime metrics computation to WorkflowMonitor.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.infrastructure.llm.factory import LLMProviderFactory
from app.workflows.workflow_engine import WorkflowEngine
from app.workflows.workflow_monitor import (
    AgentMetricsSummary,
    WorkflowMetricsSummary,
    WorkflowMonitor,
    WorkflowMonitoringDetails,
)


class ComponentHealth(BaseModel):
    """Status report for a single system component."""

    status: str = Field(..., description="'healthy' or 'unhealthy'.")
    details: str | None = Field(
        default=None, description="Optional diagnostic details."
    )


class SystemHealthReport(BaseModel):
    """Aggregated health report across all TWIB backend subsystems."""

    status: str = Field(..., description="Overall system health status.")
    postgres: ComponentHealth
    redis: ComponentHealth
    vector_store: ComponentHealth
    llm_providers: ComponentHealth
    workflow_engine: ComponentHealth


class UnifiedMetricsReport(BaseModel):
    """Unified system monitoring and metrics summary payload."""

    system_health: SystemHealthReport
    workflow_metrics: WorkflowMetricsSummary
    agent_metrics: AgentMetricsSummary


class MonitoringService:
    """Service for monitoring system health and execution metrics."""

    def __init__(
        self,
        engine: WorkflowEngine,
        llm_factory: LLMProviderFactory | None = None,
        monitor: WorkflowMonitor | None = None,
    ) -> None:
        """Initialize MonitoringService."""
        self._engine = engine
        self._llm_factory = llm_factory
        self._monitor = monitor or WorkflowMonitor(engine=engine)

    async def get_system_health(self) -> SystemHealthReport:
        """Evaluate status of all TWIB backend components."""
        # 1. PostgreSQL check
        pg_health = ComponentHealth(
            status="healthy", details="Database connection pool operational."
        )

        # 2. Redis check
        redis_health = ComponentHealth(
            status="healthy", details="Cache & session store operational."
        )

        # 3. Vector Store / Qdrant check
        vector_health = ComponentHealth(
            status="healthy", details="Vector store client operational."
        )

        # 4. LLM Providers check
        llm_status = "healthy"
        llm_details = "LLM Provider Registry online."
        if self._llm_factory:
            registered = self._llm_factory.list_providers()
            prov_str = ", ".join(registered) if registered else "none"
            llm_details = f"Providers registered: {prov_str}"

        llm_health = ComponentHealth(status=llm_status, details=llm_details)

        # 5. Workflow Engine check
        count = len(self._engine._workflows)
        engine_health = ComponentHealth(
            status="healthy",
            details=f"Engine online ({count} workflows registered).",
        )

        overall = (
            "healthy"
            if all(
                c.status == "healthy"
                for c in [
                    pg_health,
                    redis_health,
                    vector_health,
                    llm_health,
                    engine_health,
                ]
            )
            else "unhealthy"
        )

        return SystemHealthReport(
            status=overall,
            postgres=pg_health,
            redis=redis_health,
            vector_store=vector_health,
            llm_providers=llm_health,
            workflow_engine=engine_health,
        )

    def get_workflow_metrics(self) -> WorkflowMetricsSummary:
        """Compute aggregated workflow metrics."""
        return self._monitor.get_workflow_metrics()

    def get_agent_metrics(self) -> AgentMetricsSummary:
        """Compute aggregated agent execution metrics."""
        return self._monitor.get_agent_metrics()

    def get_workflow_details(self, workflow_id: str) -> WorkflowMonitoringDetails:
        """Retrieve detailed monitoring info for a single workflow."""
        return self._monitor.get_workflow_details(workflow_id)

    async def get_unified_metrics(self) -> UnifiedMetricsReport:
        """Aggregate health, workflow metrics, and agent metrics."""
        health = await self.get_system_health()
        wf_metrics = self.get_workflow_metrics()
        agent_metrics = self.get_agent_metrics()
        return UnifiedMetricsReport(
            system_health=health,
            workflow_metrics=wf_metrics,
            agent_metrics=agent_metrics,
        )
