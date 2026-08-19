"""Workflow Template models and schemas.

Defines TemplateCategory enum and WorkflowTemplateData Pydantic schema.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class TemplateCategory(StrEnum):
    """Categories for workflow template blueprints.

    Members:
        SOFTWARE_DEVELOPMENT: Full software engineering development lifecycle.
        CODE_REVIEW: Code review, linting, and architectural assessment.
        RESEARCH: Knowledge acquisition and technical research reports.
        BUSINESS_ANALYSIS: Requirements gathering and business specification.
        DOCUMENTATION: Technical, user, and API documentation generation.
        ARCHITECTURE_DESIGN: Modular system architecture design.
        SECURITY_REVIEW: Security audit, threat model, and vulnerability review.
        DATA_ANALYSIS: Data pipeline and analytical workflow synthesis.
        CUSTOM: User-defined custom orchestration templates.
    """

    SOFTWARE_DEVELOPMENT = "software_development"
    CODE_REVIEW = "code_review"
    RESEARCH = "research"
    BUSINESS_ANALYSIS = "business_analysis"
    DOCUMENTATION = "documentation"
    ARCHITECTURE_DESIGN = "architecture_design"
    SECURITY_REVIEW = "security_review"
    DATA_ANALYSIS = "data_analysis"
    CUSTOM = "custom"


class WorkflowTemplateData(BaseModel):
    """Pydantic schema representing a workflow template definition."""

    template_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique template identifier.",
    )
    template_name: str = Field(..., description="Human-readable template name.")
    description: str = Field(default="", description="Detailed template description.")
    category: TemplateCategory | str = Field(
        default=TemplateCategory.CUSTOM,
        description="Template domain category.",
    )
    workflow_definition: dict[str, Any] = Field(
        default_factory=dict,
        description="Workflow DAG structure, step list, or execution blueprint.",
    )
    default_configuration: dict[str, Any] = Field(
        default_factory=dict,
        description="Default execution context parameters and settings.",
    )
    supported_agents: list[str] = Field(
        default_factory=list,
        description="List of agent IDs utilized by this template.",
    )
    requires_approval: bool = Field(
        default=False,
        description="Whether instantiation requires human approval checkpoints.",
    )
    version: str = Field(
        default="1.0.0",
        description="Semantic version string of the template.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Creation timestamp.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Last modification timestamp.",
    )
