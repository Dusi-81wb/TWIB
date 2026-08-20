"""Tests for Workflow Domain Entities, Value Objects, Events, and Exceptions."""

from datetime import UTC, datetime
import pytest

from app.domain.entity import Identity
from app.domain.workflows.entities import (
    Workflow,
    WorkflowCheckpoint,
    WorkflowExecution,
)
from app.domain.workflows.events import (
    CheckpointApprovedEvent,
    WorkflowCompletedEvent,
    WorkflowCreatedEvent,
    WorkflowStartedEvent,
)
from app.domain.workflows.exceptions import (
    CheckpointError,
    WorkflowCycleError,
    WorkflowStateError,
    WorkflowValidationError,
)
from app.domain.workflows.value_objects import (
    ApprovalStatus,
    CheckpointType,
    EdgeType,
    NodeExecutionState,
    NodeStatus,
    WorkflowEdge,
    WorkflowStatus,
)


def test_workflow_aggregate_creation_and_events() -> None:
    """Workflow aggregate creation should record a WorkflowCreatedEvent and initialize properties."""
    wf = Workflow.create(
        name="Enterprise Procurement DAG",
        user_request="Automate invoice approvals",
        workspace_id="ws-123",
        graph_definition={"nodes": [{"node_id": "n1"}], "edges": []},
    )

    assert wf.name == "Enterprise Procurement DAG"
    assert wf.user_request == "Automate invoice approvals"
    assert wf.status == WorkflowStatus.CREATED
    assert wf.workspace_id == "ws-123"

    events = wf.pull_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], WorkflowCreatedEvent)
    assert events[0].workflow_name == "Enterprise Procurement DAG"
    assert events[0].node_count == 1


def test_workflow_validation_empty_fields() -> None:
    """Empty workflow name or user_request must raise WorkflowValidationError."""
    with pytest.raises(WorkflowValidationError):
        Workflow.create(name="", user_request="Some request")

    with pytest.raises(WorkflowValidationError):
        Workflow.create(name="Valid Name", user_request="")


def test_workflow_state_transitions() -> None:
    """Workflow aggregate enforces terminal state transition constraints."""
    wf = Workflow.create(name="Flow", user_request="Goal")
    wf.transition_to(WorkflowStatus.RUNNING)
    assert wf.status == WorkflowStatus.RUNNING

    wf.transition_to(WorkflowStatus.COMPLETED)
    assert wf.status == WorkflowStatus.COMPLETED

    # Cannot transition from terminal COMPLETED to RUNNING
    with pytest.raises(WorkflowStateError):
        wf.transition_to(WorkflowStatus.RUNNING)


def test_workflow_execution_aggregate_lifecycle() -> None:
    """WorkflowExecution tracks running, step outputs, node state snapshots, and completion."""
    exec_agg = WorkflowExecution.create(workflow_id="wf-100", context={"budget": 5000})
    assert exec_agg.status == WorkflowStatus.CREATED
    assert exec_agg.context["budget"] == 5000

    exec_agg.mark_started()
    assert exec_agg.status == WorkflowStatus.RUNNING
    assert exec_agg.started_at is not None

    n_state = NodeExecutionState(node_id="node_a")
    n_state.mark_running()
    n_state.mark_completed(outputs={"result_key": "val_123"})
    exec_agg.update_node_state(n_state)

    assert exec_agg.get_node_state("node_a") is not None
    assert exec_agg.step_outputs["node_a"] == {"result_key": "val_123"}

    exec_agg.mark_completed(final_outputs={"summary": "Approved"})
    assert exec_agg.status == WorkflowStatus.COMPLETED
    assert exec_agg.duration_seconds >= 0.0

    events = exec_agg.pull_domain_events()
    event_types = [type(e) for e in events]
    assert WorkflowStartedEvent in event_types
    assert WorkflowCompletedEvent in event_types


def test_workflow_checkpoint_entity() -> None:
    """WorkflowCheckpoint records human review decisions and state snapshots."""
    chk = WorkflowCheckpoint.create(
        workflow_id="wf-1",
        execution_id="exec-1",
        title="Approve Architecture Design",
        description="Review components before deployment",
        checkpoint_type=CheckpointType.ARCHITECTURE_APPROVAL,
        data_to_review={"diagram": "mermaid..."},
    )
    assert chk.approval_status == ApprovalStatus.PENDING

    chk.approve(reviewed_by="admin_user", comments="Looks solid!")
    assert chk.approval_status == ApprovalStatus.APPROVED
    assert chk.reviewed_by == "admin_user"
    assert chk.comments == "Looks solid!"

    # Double approval raises error
    with pytest.raises(CheckpointError):
        chk.approve(reviewed_by="admin_2")


def test_workflow_edge_value_object() -> None:
    """WorkflowEdge serializes and deserializes correctly."""
    edge = WorkflowEdge(
        source_node_id="node_1",
        target_node_id="node_2",
        edge_type=EdgeType.CONDITIONAL,
        condition_expression="decision == True",
        metadata={"priority": "high"},
    )
    data = edge.to_dict()
    assert data["source_node_id"] == "node_1"
    assert data["target_node_id"] == "node_2"
    assert data["edge_type"] == "conditional"

    restored = WorkflowEdge.from_dict(data)
    assert restored.source_node_id == edge.source_node_id
    assert restored.edge_type == EdgeType.CONDITIONAL
    assert restored.condition_expression == "decision == True"
