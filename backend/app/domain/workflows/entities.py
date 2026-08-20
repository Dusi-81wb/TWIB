"""Domain entities and aggregate roots for the Workflow Subsystem.

Defines the consistency boundaries and domain aggregates:
- `Workflow` (Aggregate Root)
- `WorkflowExecution` (Aggregate Root)
- `WorkflowCheckpoint` (Entity)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
import uuid

from app.domain.aggregate import AggregateRoot
from app.domain.entity import Entity, Identity
from app.domain.workflows.events import (
    CheckpointApprovedEvent,
    CheckpointCreatedEvent,
    CheckpointRejectedEvent,
    WorkflowCancelledEvent,
    WorkflowCompletedEvent,
    WorkflowCreatedEvent,
    WorkflowFailedEvent,
    WorkflowPausedEvent,
    WorkflowResumedEvent,
    WorkflowStartedEvent,
)
from app.domain.workflows.exceptions import (
    CheckpointError,
    WorkflowStateError,
    WorkflowValidationError,
)
from app.domain.workflows.value_objects import (
    ApprovalStatus,
    CheckpointType,
    NodeExecutionState,
    NodeStatus,
    WorkflowStatus,
)


class Workflow(AggregateRoot[str]):
    """Aggregate root representing a business workflow definition and state machine."""

    def __init__(
        self,
        id_: Identity[str],
        name: str,
        user_request: str,
        workspace_id: str | None = None,
        status: WorkflowStatus = WorkflowStatus.CREATED,
        graph_definition: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id_)
        now = datetime.now(UTC)
        self._name = name.strip() if name else ""
        self._user_request = user_request.strip() if user_request else ""
        self._workspace_id = workspace_id
        self._status = status
        self._graph_definition = graph_definition or {"nodes": [], "edges": []}
        self._metadata = metadata or {}
        self._created_at = created_at or now
        self._updated_at = updated_at or now

        if not self._name:
            raise WorkflowValidationError("Workflow name cannot be empty", workflow_id=self.id.value)
        if not self._user_request:
            raise WorkflowValidationError("Workflow user_request cannot be empty", workflow_id=self.id.value)

    @classmethod
    def create(
        cls,
        name: str,
        user_request: str,
        workspace_id: str | None = None,
        graph_definition: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        workflow_id: str | None = None,
    ) -> Workflow:
        """Factory method to instantiate and record a new Workflow aggregate."""
        wid = workflow_id or str(uuid.uuid4())
        workflow = cls(
            id_=Identity(wid),
            name=name,
            user_request=user_request,
            workspace_id=workspace_id,
            status=WorkflowStatus.CREATED,
            graph_definition=graph_definition,
            metadata=metadata,
        )
        nodes_len = len(workflow._graph_definition.get("nodes", []))
        edges_len = len(workflow._graph_definition.get("edges", []))
        workflow.record_event(
            WorkflowCreatedEvent(
                workflow_id=wid,
                workflow_name=workflow._name,
                workspace_id=workspace_id,
                node_count=nodes_len,
                edge_count=edges_len,
            )
        )
        return workflow

    @property
    def workflow_id(self) -> str:
        """Return the workflow aggregate ID string."""
        return self.id.value

    @property
    def name(self) -> str:
        return self._name

    @property
    def user_request(self) -> str:
        return self._user_request

    @property
    def workspace_id(self) -> str | None:
        return self._workspace_id

    @property
    def status(self) -> WorkflowStatus:
        return self._status

    @property
    def graph_definition(self) -> dict[str, Any]:
        return self._graph_definition

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def update_graph_definition(self, graph_def: dict[str, Any]) -> None:
        """Update the workflow DAG definition."""
        self._graph_definition = graph_def
        self._updated_at = datetime.now(UTC)

    def update_metadata(self, metadata: dict[str, Any]) -> None:
        """Merge or update metadata."""
        self._metadata.update(metadata)
        self._updated_at = datetime.now(UTC)

    def transition_to(self, new_status: WorkflowStatus) -> None:
        """Transition workflow status enforcing valid domain transition rules."""
        terminal_states = {WorkflowStatus.COMPLETED, WorkflowStatus.CANCELLED}
        if self._status in terminal_states and new_status not in terminal_states:
            raise WorkflowStateError(
                f"Cannot transition from terminal state '{self._status}' to '{new_status}'",
                workflow_id=self.workflow_id,
                from_state=str(self._status),
                to_state=str(new_status),
            )
        self._status = new_status
        self._updated_at = datetime.now(UTC)


class WorkflowExecution(AggregateRoot[str]):
    """Aggregate root managing the lifecycle, runtime state, and telemetry of a single DAG run."""

    def __init__(
        self,
        id_: Identity[str],
        workflow_id: str,
        status: WorkflowStatus = WorkflowStatus.CREATED,
        context: dict[str, Any] | None = None,
        node_states: dict[str, NodeExecutionState] | None = None,
        step_outputs: dict[str, Any] | None = None,
        error: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        duration_seconds: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(id_)
        self._workflow_id = workflow_id
        self._status = status
        self._context = context or {}
        self._node_states: dict[str, NodeExecutionState] = node_states or {}
        self._step_outputs: dict[str, Any] = step_outputs or {}
        self._error = error
        self._started_at = started_at
        self._completed_at = completed_at
        self._duration_seconds = duration_seconds
        self._metadata = metadata or {}

    @classmethod
    def create(
        cls,
        workflow_id: str,
        context: dict[str, Any] | None = None,
        execution_id: str | None = None,
    ) -> WorkflowExecution:
        """Factory method creating a new WorkflowExecution aggregate."""
        eid = execution_id or str(uuid.uuid4())
        return cls(
            id_=Identity(eid),
            workflow_id=workflow_id,
            status=WorkflowStatus.CREATED,
            context=context or {},
        )

    @property
    def execution_id(self) -> str:
        return self.id.value

    @property
    def workflow_id(self) -> str:
        return self._workflow_id

    @property
    def status(self) -> WorkflowStatus:
        return self._status

    @property
    def context(self) -> dict[str, Any]:
        return self._context

    @property
    def node_states(self) -> dict[str, NodeExecutionState]:
        return self._node_states

    @property
    def step_outputs(self) -> dict[str, Any]:
        return self._step_outputs

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def started_at(self) -> datetime | None:
        return self._started_at

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at

    @property
    def duration_seconds(self) -> float:
        return self._duration_seconds

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    def mark_started(self) -> None:
        """Mark execution as active."""
        self._status = WorkflowStatus.RUNNING
        self._started_at = datetime.now(UTC)
        self.record_event(
            WorkflowStartedEvent(
                workflow_id=self._workflow_id,
                execution_id=self.execution_id,
                started_at=self._started_at,
            )
        )

    def mark_paused(self, checkpoint_id: str, reason: str = "Awaiting human review") -> None:
        """Mark execution paused for approval checkpoint."""
        self._status = WorkflowStatus.WAITING_FOR_APPROVAL
        self.record_event(
            WorkflowPausedEvent(
                workflow_id=self._workflow_id,
                execution_id=self.execution_id,
                checkpoint_id=checkpoint_id,
                reason=reason,
            )
        )

    def mark_resumed(self, checkpoint_id: str | None = None, resumed_by: str | None = None) -> None:
        """Mark execution resumed."""
        self._status = WorkflowStatus.RUNNING
        self.record_event(
            WorkflowResumedEvent(
                workflow_id=self._workflow_id,
                execution_id=self.execution_id,
                checkpoint_id=checkpoint_id,
                resumed_by=resumed_by,
            )
        )

    def mark_completed(self, final_outputs: dict[str, Any] | None = None) -> None:
        """Mark execution completed successfully."""
        self._status = WorkflowStatus.COMPLETED
        self._completed_at = datetime.now(UTC)
        if self._started_at:
            self._duration_seconds = (self._completed_at - self._started_at).total_seconds()
        if final_outputs:
            self._step_outputs.update(final_outputs)
        self.record_event(
            WorkflowCompletedEvent(
                workflow_id=self._workflow_id,
                execution_id=self.execution_id,
                duration_seconds=self._duration_seconds,
                outputs=dict(self._step_outputs),
                completed_at=self._completed_at,
            )
        )

    def mark_failed(self, error: str, failed_node_id: str | None = None) -> None:
        """Mark execution failed."""
        self._status = WorkflowStatus.FAILED
        self._error = error
        self._completed_at = datetime.now(UTC)
        if self._started_at:
            self._duration_seconds = (self._completed_at - self._started_at).total_seconds()
        self.record_event(
            WorkflowFailedEvent(
                workflow_id=self._workflow_id,
                execution_id=self.execution_id,
                error=error,
                failed_node_id=failed_node_id,
                failed_at=self._completed_at,
            )
        )

    def mark_cancelled(self, cancelled_by: str | None = None) -> None:
        """Mark execution cancelled."""
        self._status = WorkflowStatus.CANCELLED
        self._completed_at = datetime.now(UTC)
        if self._started_at:
            self._duration_seconds = (self._completed_at - self._started_at).total_seconds()
        self.record_event(
            WorkflowCancelledEvent(
                workflow_id=self._workflow_id,
                execution_id=self.execution_id,
                cancelled_by=cancelled_by,
                cancelled_at=self._completed_at,
            )
        )

    def update_node_state(self, state: NodeExecutionState) -> None:
        """Upsert a node execution snapshot."""
        self._node_states[state.node_id] = state
        if state.status == NodeStatus.COMPLETED and state.outputs:
            self._step_outputs[state.node_id] = state.outputs

    def get_node_state(self, node_id: str) -> NodeExecutionState | None:
        """Retrieve node execution state if exists."""
        return self._node_states.get(node_id)


class WorkflowCheckpoint(Entity[str]):
    """Entity representing a human approval checkpoint or state recovery point."""

    def __init__(
        self,
        id_: Identity[str],
        workflow_id: str,
        execution_id: str,
        step_id: str | None = None,
        checkpoint_type: CheckpointType | str = CheckpointType.HUMAN_APPROVAL,
        approval_status: ApprovalStatus = ApprovalStatus.PENDING,
        title: str = "",
        description: str = "",
        data_to_review: dict[str, Any] | None = None,
        state_snapshot: dict[str, Any] | None = None,
        assigned_role: str | None = None,
        requested_by: str | None = None,
        reviewed_by: str | None = None,
        comments: str | None = None,
        created_at: datetime | None = None,
        reviewed_at: datetime | None = None,
    ) -> None:
        super().__init__(id_)
        now = datetime.now(UTC)
        self._workflow_id = workflow_id
        self._execution_id = execution_id
        self._step_id = step_id
        self._checkpoint_type = checkpoint_type
        self._approval_status = approval_status
        self._title = title
        self._description = description
        self._data_to_review = data_to_review or {}
        self._state_snapshot = state_snapshot or {}
        self._assigned_role = assigned_role
        self._requested_by = requested_by
        self._reviewed_by = reviewed_by
        self._comments = comments
        self._created_at = created_at or now
        self._reviewed_at = reviewed_at

    @classmethod
    def create(
        cls,
        workflow_id: str,
        execution_id: str,
        title: str,
        description: str = "",
        step_id: str | None = None,
        checkpoint_type: CheckpointType | str = CheckpointType.HUMAN_APPROVAL,
        data_to_review: dict[str, Any] | None = None,
        state_snapshot: dict[str, Any] | None = None,
        assigned_role: str | None = None,
        requested_by: str | None = None,
        checkpoint_id: str | None = None,
    ) -> WorkflowCheckpoint:
        """Factory method to instantiate a new WorkflowCheckpoint."""
        cid = checkpoint_id or str(uuid.uuid4())
        return cls(
            id_=Identity(cid),
            workflow_id=workflow_id,
            execution_id=execution_id,
            step_id=step_id,
            checkpoint_type=checkpoint_type,
            approval_status=ApprovalStatus.PENDING,
            title=title,
            description=description,
            data_to_review=data_to_review,
            state_snapshot=state_snapshot,
            assigned_role=assigned_role,
            requested_by=requested_by,
        )

    @property
    def checkpoint_id(self) -> str:
        return self.id.value

    @property
    def workflow_id(self) -> str:
        return self._workflow_id

    @property
    def execution_id(self) -> str:
        return self._execution_id

    @property
    def step_id(self) -> str | None:
        return self._step_id

    @property
    def checkpoint_type(self) -> CheckpointType | str:
        return self._checkpoint_type

    @property
    def approval_status(self) -> ApprovalStatus:
        return self._approval_status

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def data_to_review(self) -> dict[str, Any]:
        return self._data_to_review

    @property
    def state_snapshot(self) -> dict[str, Any]:
        return self._state_snapshot

    @property
    def assigned_role(self) -> str | None:
        return self._assigned_role

    @property
    def requested_by(self) -> str | None:
        return self._requested_by

    @property
    def reviewed_by(self) -> str | None:
        return self._reviewed_by

    @property
    def comments(self) -> str | None:
        return self._comments

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def reviewed_at(self) -> datetime | None:
        return self._reviewed_at

    def approve(self, reviewed_by: str, comments: str | None = None) -> None:
        """Record reviewer approval."""
        if self._approval_status != ApprovalStatus.PENDING:
            raise CheckpointError(
                f"Checkpoint {self.checkpoint_id} is already in {self._approval_status} status",
                checkpoint_id=self.checkpoint_id,
            )
        self._approval_status = ApprovalStatus.APPROVED
        self._reviewed_by = reviewed_by
        self._comments = comments
        self._reviewed_at = datetime.now(UTC)

    def reject(self, reviewed_by: str, comments: str | None = None) -> None:
        """Record reviewer rejection."""
        if self._approval_status != ApprovalStatus.PENDING:
            raise CheckpointError(
                f"Checkpoint {self.checkpoint_id} is already in {self._approval_status} status",
                checkpoint_id=self.checkpoint_id,
            )
        self._approval_status = ApprovalStatus.REJECTED
        self._reviewed_by = reviewed_by
        self._comments = comments
        self._reviewed_at = datetime.now(UTC)

    def request_changes(self, reviewed_by: str, comments: str) -> None:
        """Record request for changes."""
        if self._approval_status != ApprovalStatus.PENDING:
            raise CheckpointError(
                f"Checkpoint {self.checkpoint_id} is already in {self._approval_status} status",
                checkpoint_id=self.checkpoint_id,
            )
        self._approval_status = ApprovalStatus.CHANGES_REQUESTED
        self._reviewed_by = reviewed_by
        self._comments = comments
        self._reviewed_at = datetime.now(UTC)
