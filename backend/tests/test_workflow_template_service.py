"""Tests for WorkflowTemplate and WorkflowTemplateService implementation."""

import pytest

from app.workflows import (
    TemplateCategory,
    WorkflowEngine,
    WorkflowNotFoundError,
    WorkflowStatus,
    WorkflowTemplateService,
    WorkflowValidationError,
)


def test_builtin_templates_registered() -> None:
    service = WorkflowTemplateService()
    templates = service.list_templates()
    assert len(templates) >= 8

    # Verify built-in categories present
    categories = {t.category for t in templates}
    assert TemplateCategory.SOFTWARE_DEVELOPMENT in categories
    assert TemplateCategory.CODE_REVIEW in categories
    assert TemplateCategory.RESEARCH in categories
    assert TemplateCategory.BUSINESS_ANALYSIS in categories
    assert TemplateCategory.DOCUMENTATION in categories
    assert TemplateCategory.ARCHITECTURE_DESIGN in categories
    assert TemplateCategory.SECURITY_REVIEW in categories
    assert TemplateCategory.DATA_ANALYSIS in categories


def test_template_crud_operations() -> None:
    service = WorkflowTemplateService()

    # Unauthorized creation check
    with pytest.raises(WorkflowValidationError):
        service.create_template(
            template_name="Custom Tpl",
            description="Test custom",
            user_roles=["viewer"],
        )

    # Authorized creation
    tpl = service.create_template(
        template_name="Custom Admin Pipeline",
        description="Admin custom pipeline",
        category=TemplateCategory.CUSTOM,
        workflow_definition={"steps": [{"name": "Custom Step", "agent_id": "planner"}]},
        user_roles=["admin"],
    )
    assert tpl.template_id is not None
    assert tpl.template_name == "Custom Admin Pipeline"

    # Update template
    updated_tpl = service.update_template(
        tpl.template_id,
        description="Updated description",
        user_roles=["owner"],
    )
    assert updated_tpl.description == "Updated description"

    # Get template
    loaded = service.get_template(tpl.template_id)
    assert loaded.template_id == tpl.template_id

    # Delete template
    assert service.delete_template(tpl.template_id, user_roles=["admin"]) is True
    with pytest.raises(WorkflowNotFoundError):
        service.get_template(tpl.template_id)


def test_instantiate_workflow_from_template() -> None:
    engine = WorkflowEngine()
    service = WorkflowTemplateService(engine=engine)

    wf = service.instantiate_workflow(
        template_id="tpl-software-dev",
        user_request="Build new web application backend",
        custom_name="Web App Dev Instance",
        configuration_overrides={"target_env": "production"},
    )

    assert wf.workflow_id is not None
    assert wf.workflow_name == "Web App Dev Instance"
    assert wf.user_request == "Build new web application backend"
    assert wf.workflow_status == WorkflowStatus.CREATED
    assert len(wf.execution_steps) == 7
    assert wf.metadata["template_id"] == "tpl-software-dev"
    assert wf.metadata["context"]["target_env"] == "production"
