"""Workflow Template domain model and built-in templates.

Encapsulates workflow template properties, instantiation helpers, and built-ins.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.workflows.workflow_models import WorkflowStep
from app.workflows.workflow_template_models import (
    TemplateCategory,
    WorkflowTemplateData,
)


class WorkflowTemplate:
    """Domain representation of a reusable Workflow Template blueprint."""

    def __init__(
        self,
        template_name: str,
        description: str,
        category: TemplateCategory | str = TemplateCategory.CUSTOM,
        template_id: str | None = None,
        workflow_definition: dict[str, Any] | None = None,
        default_configuration: dict[str, Any] | None = None,
        supported_agents: list[str] | None = None,
        requires_approval: bool = False,
        version: str = "1.0.0",
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize WorkflowTemplate.

        Args:
            template_name: Name of the template.
            description: Description of template purpose.
            category: Domain category.
            template_id: Unique template identifier.
            workflow_definition: Workflow DAG structure or step list.
            default_configuration: Default context parameters.
            supported_agents: List of agent IDs used in pipeline.
            requires_approval: Flag indicating if checkpoints are required.
            version: Semantic version string.
            created_at: Creation timestamp.
            updated_at: Last modification timestamp.
        """
        now = datetime.now(UTC)
        self.template_id = template_id or str(uuid.uuid4())
        self.template_name = template_name
        self.description = description
        self.category = category
        self.workflow_definition: dict[str, Any] = workflow_definition or {}
        self.default_configuration: dict[str, Any] = default_configuration or {}
        self.supported_agents: list[str] = supported_agents or []
        self.requires_approval = requires_approval
        self.version = version
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def generate_steps(self) -> list[WorkflowStep]:
        """Generate WorkflowStep instances based on workflow_definition."""
        steps_raw = self.workflow_definition.get("steps", [])
        steps: list[WorkflowStep] = []
        for s in steps_raw:
            agent_id = s.get("agent_id")
            step_name = s.get("name", f"Execute {agent_id or 'Step'}")
            steps.append(
                WorkflowStep(
                    name=step_name,
                    agent_id=agent_id,
                    input_data=s.get("input_data", {}),
                )
            )
        return steps

    def to_model(self) -> WorkflowTemplateData:
        """Serialize domain WorkflowTemplate into Pydantic schema."""
        return WorkflowTemplateData(
            template_id=self.template_id,
            template_name=self.template_name,
            description=self.description,
            category=self.category,
            workflow_definition=self.workflow_definition,
            default_configuration=self.default_configuration,
            supported_agents=self.supported_agents,
            requires_approval=self.requires_approval,
            version=self.version,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_model(cls, model: WorkflowTemplateData) -> WorkflowTemplate:
        """Instantiate domain WorkflowTemplate from Pydantic schema."""
        return cls(
            template_id=model.template_id,
            template_name=model.template_name,
            description=model.description,
            category=model.category,
            workflow_definition=model.workflow_definition,
            default_configuration=model.default_configuration,
            supported_agents=model.supported_agents,
            requires_approval=model.requires_approval,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


def get_builtin_templates() -> list[WorkflowTemplate]:
    """Retrieve pre-built system workflow templates.

    Returns:
        List of built-in WorkflowTemplate instances for core workflows.
    """
    templates: list[WorkflowTemplate] = [
        WorkflowTemplate(
            template_id="tpl-software-dev",
            template_name="Software Development",
            description="End-to-end software engineering pipeline.",
            category=TemplateCategory.SOFTWARE_DEVELOPMENT,
            supported_agents=[
                "planner",
                "research",
                "analyst",
                "architect",
                "validator",
                "optimizer",
                "documentation",
            ],
            requires_approval=True,
            workflow_definition={
                "steps": [
                    {"name": "Decompose Goal", "agent_id": "planner"},
                    {"name": "Gather Knowledge", "agent_id": "research"},
                    {"name": "Synthesize Requirements", "agent_id": "analyst"},
                    {"name": "Design Architecture", "agent_id": "architect"},
                    {"name": "Quality Audit", "agent_id": "validator"},
                    {"name": "Refine Content", "agent_id": "optimizer"},
                    {"name": "Generate Docs", "agent_id": "documentation"},
                ]
            },
        ),
        WorkflowTemplate(
            template_id="tpl-code-review",
            template_name="Code Review",
            description="Automated code review and quality checks.",
            category=TemplateCategory.CODE_REVIEW,
            supported_agents=["analyst", "validator", "optimizer"],
            requires_approval=False,
            workflow_definition={
                "steps": [
                    {"name": "Analyze Code Structure", "agent_id": "analyst"},
                    {"name": "Validate Quality & Lints", "agent_id": "validator"},
                    {"name": "Optimize Readability", "agent_id": "optimizer"},
                ]
            },
        ),
        WorkflowTemplate(
            template_id="tpl-research",
            template_name="Research",
            description="Domain information gathering and reporting.",
            category=TemplateCategory.RESEARCH,
            supported_agents=["planner", "research", "documentation"],
            requires_approval=False,
            workflow_definition={
                "steps": [
                    {"name": "Formulate Search Strategy", "agent_id": "planner"},
                    {"name": "Collect Knowledge", "agent_id": "research"},
                    {"name": "Generate Summary Report", "agent_id": "documentation"},
                ]
            },
        ),
        WorkflowTemplate(
            template_id="tpl-business-analysis",
            template_name="Business Analysis",
            description="Requirements analysis and scope definition.",
            category=TemplateCategory.BUSINESS_ANALYSIS,
            supported_agents=["planner", "analyst", "documentation"],
            requires_approval=False,
            workflow_definition={
                "steps": [
                    {"name": "Decompose Objectives", "agent_id": "planner"},
                    {"name": "Formulate Specifications", "agent_id": "analyst"},
                    {"name": "Produce Business Spec", "agent_id": "documentation"},
                ]
            },
        ),
        WorkflowTemplate(
            template_id="tpl-documentation",
            template_name="Documentation",
            description="Technical documentation generation.",
            category=TemplateCategory.DOCUMENTATION,
            supported_agents=["analyst", "optimizer", "documentation"],
            requires_approval=False,
            workflow_definition={
                "steps": [
                    {"name": "Extract Technical Points", "agent_id": "analyst"},
                    {"name": "Refine Clarity", "agent_id": "optimizer"},
                    {"name": "Format Documentation", "agent_id": "documentation"},
                ]
            },
        ),
        WorkflowTemplate(
            template_id="tpl-architecture-design",
            template_name="Architecture Design",
            description="High-level modular system architecture design.",
            category=TemplateCategory.ARCHITECTURE_DESIGN,
            supported_agents=["analyst", "architect", "validator"],
            requires_approval=True,
            workflow_definition={
                "steps": [
                    {"name": "Analyze Requirements", "agent_id": "analyst"},
                    {"name": "Generate Modular Architecture", "agent_id": "architect"},
                    {
                        "name": "Validate Scalability & Security",
                        "agent_id": "validator",
                    },
                ]
            },
        ),
        WorkflowTemplate(
            template_id="tpl-security-review",
            template_name="Security Review",
            description="Threat modeling and security audit.",
            category=TemplateCategory.SECURITY_REVIEW,
            supported_agents=["architect", "validator", "documentation"],
            requires_approval=True,
            workflow_definition={
                "steps": [
                    {
                        "name": "Inspect Architecture & Boundaries",
                        "agent_id": "architect",
                    },
                    {"name": "Audit Security & Controls", "agent_id": "validator"},
                    {
                        "name": "Document Security Assessment",
                        "agent_id": "documentation",
                    },
                ]
            },
        ),
        WorkflowTemplate(
            template_id="tpl-data-analysis",
            template_name="Data Analysis",
            description="Data pipeline modeling and analytical reporting.",
            category=TemplateCategory.DATA_ANALYSIS,
            supported_agents=["research", "analyst", "optimizer"],
            requires_approval=False,
            workflow_definition={
                "steps": [
                    {"name": "Gather Data Sources", "agent_id": "research"},
                    {"name": "Analyze Patterns & Metrics", "agent_id": "analyst"},
                    {"name": "Synthesize Insights", "agent_id": "optimizer"},
                ]
            },
        ),
    ]
    return templates
