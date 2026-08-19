"""Workflow Template Service implementation.

Manages creation, update, deletion, listing, and instantiation of templates
with RBAC authorization controls and audit logging.
"""

from __future__ import annotations

from typing import Any

from app.authorization.roles import is_org_role_at_least, is_workspace_role_at_least
from app.services.audit.audit_service import AuditService
from app.workflows.workflow import Workflow
from app.workflows.workflow_engine import WorkflowEngine
from app.workflows.workflow_exceptions import (
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from app.workflows.workflow_template import (
    WorkflowTemplate,
    get_builtin_templates,
)
from app.workflows.workflow_template_models import TemplateCategory


class WorkflowTemplateService:
    """Service managing Workflow Template blueprints and workflow instantiation."""

    def __init__(
        self,
        engine: WorkflowEngine | None = None,
        audit_service: AuditService | None = None,
    ) -> None:
        """Initialize WorkflowTemplateService and seed built-in system templates.

        Args:
            engine: Optional WorkflowEngine instance.
            audit_service: Optional AuditService instance.
        """
        self._engine = engine or WorkflowEngine()
        self._audit_service = audit_service or AuditService()
        self._templates: dict[str, WorkflowTemplate] = {}

        # Seed built-in templates
        for tpl in get_builtin_templates():
            self._templates[tpl.template_id] = tpl

    def create_template(
        self,
        template_name: str,
        description: str,
        category: TemplateCategory | str = TemplateCategory.CUSTOM,
        workflow_definition: dict[str, Any] | None = None,
        default_configuration: dict[str, Any] | None = None,
        supported_agents: list[str] | None = None,
        requires_approval: bool = False,
        version: str = "1.0.0",
        user_roles: list[str] | None = None,
    ) -> WorkflowTemplate:
        """Create and register a new Workflow Template.

        Args:
            template_name: Name of the template.
            description: Description of template purpose.
            category: Domain category.
            workflow_definition: Pipeline structure or step list.
            default_configuration: Default context parameters.
            supported_agents: Agent IDs utilized by template.
            requires_approval: Flag indicating if approval checkpoints are required.
            version: Semantic version string.
            user_roles: Roles held by caller for RBAC validation.

        Returns:
            Created WorkflowTemplate instance.

        Raises:
            WorkflowValidationError: If user is unauthorized or name is empty.
        """
        self._authorize_management(user_roles)

        if not template_name or not template_name.strip():
            raise WorkflowValidationError(
                "Template name cannot be empty", workflow_id="unknown"
            )

        template = WorkflowTemplate(
            template_name=template_name.strip(),
            description=description,
            category=category,
            workflow_definition=workflow_definition,
            default_configuration=default_configuration,
            supported_agents=supported_agents,
            requires_approval=requires_approval,
            version=version,
        )
        self._templates[template.template_id] = template
        return template

    def update_template(
        self,
        template_id: str,
        template_name: str | None = None,
        description: str | None = None,
        category: TemplateCategory | str | None = None,
        workflow_definition: dict[str, Any] | None = None,
        default_configuration: dict[str, Any] | None = None,
        supported_agents: list[str] | None = None,
        requires_approval: bool | None = None,
        version: str | None = None,
        user_roles: list[str] | None = None,
    ) -> WorkflowTemplate:
        """Update an existing Workflow Template.

        Args:
            template_id: Target template identifier.
            template_name: Optional new template name.
            description: Optional new description.
            category: Optional new category.
            workflow_definition: Optional new workflow definition.
            default_configuration: Optional new default configuration.
            supported_agents: Optional new list of supported agents.
            requires_approval: Optional new approval requirement flag.
            version: Optional new version string.
            user_roles: Roles held by caller for RBAC validation.

        Returns:
            Updated WorkflowTemplate instance.

        Raises:
            WorkflowNotFoundError: If template ID is not found.
            WorkflowValidationError: If user is unauthorized.
        """
        self._authorize_management(user_roles)
        template = self.get_template(template_id)

        if template_name is not None and template_name.strip():
            template.template_name = template_name.strip()
        if description is not None:
            template.description = description
        if category is not None:
            template.category = category
        if workflow_definition is not None:
            template.workflow_definition = workflow_definition
        if default_configuration is not None:
            template.default_configuration = default_configuration
        if supported_agents is not None:
            template.supported_agents = supported_agents
        if requires_approval is not None:
            template.requires_approval = requires_approval
        if version is not None:
            template.version = version

        return template

    def delete_template(
        self,
        template_id: str,
        user_roles: list[str] | None = None,
    ) -> bool:
        """Delete an existing Workflow Template.

        Args:
            template_id: Target template identifier.
            user_roles: Roles held by caller for RBAC validation.

        Returns:
            True if template existed and was deleted, False otherwise.

        Raises:
            WorkflowValidationError: If user is unauthorized.
        """
        self._authorize_management(user_roles)
        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False

    def list_templates(
        self,
        category: TemplateCategory | str | None = None,
    ) -> list[WorkflowTemplate]:
        """List registered workflow templates, optionally filtered by category.

        Args:
            category: Optional TemplateCategory to filter by.

        Returns:
            List of matching WorkflowTemplate instances.
        """
        all_templates = list(self._templates.values())
        if not category:
            return all_templates
        cat_str = (
            category.value if isinstance(category, TemplateCategory) else str(category)
        )
        return [
            t
            for t in all_templates
            if (
                t.category.value
                if isinstance(t.category, TemplateCategory)
                else str(t.category)
            )
            == cat_str
        ]

    def get_template(self, template_id: str) -> WorkflowTemplate:
        """Retrieve a specific Workflow Template by its unique ID.

        Args:
            template_id: Unique template identifier.

        Returns:
            Loaded WorkflowTemplate instance.

        Raises:
            WorkflowNotFoundError: If template ID is not found.
        """
        if template_id not in self._templates:
            raise WorkflowNotFoundError(
                f"Template '{template_id}' not found",
                workflow_id="unknown",
            )
        return self._templates[template_id]

    def instantiate_workflow(
        self,
        template_id: str,
        user_request: str,
        custom_name: str | None = None,
        configuration_overrides: dict[str, Any] | None = None,
    ) -> Workflow:
        """Instantiate a new runnable Workflow from a Workflow Template.

        Args:
            template_id: Unique template identifier.
            user_request: User goal prompt or instructions.
            custom_name: Optional custom workflow name override.
            configuration_overrides: Optional context configuration overrides.

        Returns:
            Created Workflow domain instance.

        Raises:
            WorkflowNotFoundError: If template ID is missing.
            WorkflowValidationError: If user_request is empty.
        """
        template = self.get_template(template_id)
        name = custom_name or template.template_name
        steps = template.generate_steps()

        merged_cfg = dict(template.default_configuration)
        if configuration_overrides:
            merged_cfg.update(configuration_overrides)

        metadata: dict[str, Any] = {
            "template_id": template.template_id,
            "template_name": template.template_name,
            "template_version": template.version,
            "requires_approval": template.requires_approval,
            "context": merged_cfg,
        }

        workflow = self._engine.create_workflow(
            workflow_name=name,
            user_request=user_request,
            steps=steps,
            metadata=metadata,
        )
        return workflow

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _authorize_management(user_roles: list[str] | None) -> None:
        """Validate RBAC authorization for template CRUD management operations."""
        if not user_roles:
            raise WorkflowValidationError(
                "Administrative roles required for template management"
            )

        required_roles = ["admin", "owner"]
        authorized = False
        for role in user_roles:
            role_clean = role.lower()
            if (
                role_clean in required_roles
                or is_org_role_at_least(role_clean, "admin")
                or is_workspace_role_at_least(role_clean, "admin")
            ):
                authorized = True
                break

        if not authorized:
            err_msg = f"User roles {user_roles} unauthorized for template management"
            raise WorkflowValidationError(err_msg)
