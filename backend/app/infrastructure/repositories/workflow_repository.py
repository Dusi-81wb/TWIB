"""SQLAlchemy Repositories for Workflow Aggregates and Executions.

Implements IWorkflowRepository, IWorkflowExecutionRepository, and IWorkflowCheckpointRepository.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entity import Identity
from app.domain.workflows.entities import (
    Workflow,
    WorkflowCheckpoint,
    WorkflowExecution,
)
from app.domain.workflows.repositories import (
    IWorkflowCheckpointRepository,
    IWorkflowExecutionRepository,
    IWorkflowRepository,
)
from app.domain.workflows.value_objects import (
    ApprovalStatus,
    CheckpointType,
    NodeExecutionState,
    WorkflowStatus,
)
from app.infrastructure.database.models.workflow_model import (
    WorkflowCheckpointModel,
    WorkflowExecutionModel,
    WorkflowModel,
)
from app.infrastructure.repositories.base_repository import BaseRepository


class WorkflowRepository(BaseRepository[Workflow, WorkflowModel, str], IWorkflowRepository):
    """SQLAlchemy implementation of IWorkflowRepository."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WorkflowModel)

    def _to_domain(self, model: WorkflowModel) -> Workflow:
        status_val = WorkflowStatus(model.status) if model.status in [s.value for s in WorkflowStatus] else WorkflowStatus.CREATED
        return Workflow(
            id_=Identity(str(model.id)),
            name=model.name,
            user_request=model.user_request,
            workspace_id=str(model.workspace_id) if model.workspace_id else None,
            status=status_val,
            graph_definition=model.graph_definition or {"nodes": [], "edges": []},
            metadata=model.metadata_json or {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Workflow, existing: WorkflowModel | None = None) -> WorkflowModel:
        wid_uuid = uuid.UUID(entity.workflow_id) if isinstance(entity.workflow_id, str) and len(entity.workflow_id) == 36 else uuid.uuid4()
        workspace_uuid = uuid.UUID(entity.workspace_id) if entity.workspace_id and len(entity.workspace_id) == 36 else None

        if existing:
            existing.name = entity.name
            existing.user_request = entity.user_request
            existing.status = str(entity.status.value if hasattr(entity.status, "value") else entity.status)
            existing.graph_definition = entity.graph_definition
            existing.metadata_json = entity.metadata
            existing.workspace_id = workspace_uuid
            return existing

        return WorkflowModel(
            id=wid_uuid,
            workspace_id=workspace_uuid,
            name=entity.name,
            user_request=entity.user_request,
            status=str(entity.status.value if hasattr(entity.status, "value") else entity.status),
            graph_definition=entity.graph_definition,
            metadata=entity.metadata,
        )

    async def get_by_id(self, id_: str) -> Workflow | None:
        try:
            val_uuid = uuid.UUID(id_)
        except ValueError:
            return None
        stmt = select(WorkflowModel).where(WorkflowModel.id == val_uuid)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_workspace(
        self,
        workspace_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Workflow]:
        stmt = select(WorkflowModel)
        if workspace_id:
            try:
                ws_uuid = uuid.UUID(workspace_id)
                stmt = stmt.where(WorkflowModel.workspace_id == ws_uuid)
            except ValueError:
                pass
        stmt = stmt.order_by(WorkflowModel.created_at.desc()).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def count_by_workspace(self, workspace_id: str | None = None) -> int:
        stmt = select(func.count(WorkflowModel.id))
        if workspace_id:
            try:
                ws_uuid = uuid.UUID(workspace_id)
                stmt = stmt.where(WorkflowModel.workspace_id == ws_uuid)
            except ValueError:
                pass
        result = await self._session.execute(stmt)
        return int(result.scalar() or 0)


class WorkflowExecutionRepository(
    BaseRepository[WorkflowExecution, WorkflowExecutionModel, str],
    IWorkflowExecutionRepository,
):
    """SQLAlchemy implementation of IWorkflowExecutionRepository."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WorkflowExecutionModel)

    def _to_domain(self, model: WorkflowExecutionModel) -> WorkflowExecution:
        status_val = (
            WorkflowStatus(model.status)
            if model.status in [s.value for s in WorkflowStatus]
            else WorkflowStatus.CREATED
        )
        node_states = {
            nid: NodeExecutionState.from_dict(raw_s)
            for nid, raw_s in (model.node_states or {}).items()
        }
        return WorkflowExecution(
            id_=Identity(str(model.id)),
            workflow_id=str(model.workflow_id),
            status=status_val,
            context=model.context or {},
            node_states=node_states,
            step_outputs=model.step_outputs or {},
            error=model.error,
            started_at=model.started_at,
            completed_at=model.completed_at,
            duration_seconds=model.duration_seconds or 0.0,
            metadata=model.metadata_json or {},
        )

    def _to_model(
        self,
        entity: WorkflowExecution,
        existing: WorkflowExecutionModel | None = None,
    ) -> WorkflowExecutionModel:
        eid_uuid = uuid.UUID(entity.execution_id) if len(entity.execution_id) == 36 else uuid.uuid4()
        wf_uuid = uuid.UUID(entity.workflow_id) if len(entity.workflow_id) == 36 else uuid.uuid4()
        node_states_raw = {nid: s.to_dict() for nid, s in entity.node_states.items()}

        if existing:
            existing.status = str(entity.status.value if hasattr(entity.status, "value") else entity.status)
            existing.context = entity.context
            existing.node_states = node_states_raw
            existing.step_outputs = entity.step_outputs
            existing.error = entity.error
            existing.duration_seconds = entity.duration_seconds
            existing.started_at = entity.started_at
            existing.completed_at = entity.completed_at
            existing.metadata_json = entity.metadata
            return existing

        return WorkflowExecutionModel(
            id=eid_uuid,
            workflow_id=wf_uuid,
            status=str(entity.status.value if hasattr(entity.status, "value") else entity.status),
            context=entity.context,
            node_states=node_states_raw,
            step_outputs=entity.step_outputs,
            error=entity.error,
            duration_seconds=entity.duration_seconds,
            started_at=entity.started_at,
            completed_at=entity.completed_at,
            metadata=entity.metadata,
        )

    async def get_by_id(self, id_: str) -> WorkflowExecution | None:
        try:
            val_uuid = uuid.UUID(id_)
        except ValueError:
            return None
        stmt = select(WorkflowExecutionModel).where(WorkflowExecutionModel.id == val_uuid)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_workflow(
        self,
        workflow_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[WorkflowExecution]:
        try:
            wf_uuid = uuid.UUID(workflow_id)
        except ValueError:
            return []
        stmt = (
            select(WorkflowExecutionModel)
            .where(WorkflowExecutionModel.workflow_id == wf_uuid)
            .order_by(WorkflowExecutionModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_latest_by_workflow(self, workflow_id: str) -> WorkflowExecution | None:
        try:
            wf_uuid = uuid.UUID(workflow_id)
        except ValueError:
            return None
        stmt = (
            select(WorkflowExecutionModel)
            .where(WorkflowExecutionModel.workflow_id == wf_uuid)
            .order_by(WorkflowExecutionModel.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None


class WorkflowCheckpointRepository(
    BaseRepository[WorkflowCheckpoint, WorkflowCheckpointModel, str],
    IWorkflowCheckpointRepository,
):
    """SQLAlchemy implementation of IWorkflowCheckpointRepository."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WorkflowCheckpointModel)

    def _to_domain(self, model: WorkflowCheckpointModel) -> WorkflowCheckpoint:
        status_val = (
            ApprovalStatus(model.approval_status)
            if model.approval_status in [s.value for s in ApprovalStatus]
            else ApprovalStatus.PENDING
        )
        return WorkflowCheckpoint(
            id_=Identity(str(model.id)),
            workflow_id=str(model.workflow_id),
            execution_id=str(model.execution_id),
            step_id=model.step_id,
            checkpoint_type=model.checkpoint_type,
            approval_status=status_val,
            title=model.title,
            description=model.description or "",
            data_to_review=model.data_to_review or {},
            state_snapshot=model.state_snapshot or {},
            assigned_role=model.assigned_role,
            requested_by=model.requested_by,
            reviewed_by=model.reviewed_by,
            comments=model.comments,
            created_at=model.created_at,
            reviewed_at=model.reviewed_at,
        )

    def _to_model(
        self,
        entity: WorkflowCheckpoint,
        existing: WorkflowCheckpointModel | None = None,
    ) -> WorkflowCheckpointModel:
        cid_uuid = uuid.UUID(entity.checkpoint_id) if len(entity.checkpoint_id) == 36 else uuid.uuid4()
        wf_uuid = uuid.UUID(entity.workflow_id) if len(entity.workflow_id) == 36 else uuid.uuid4()
        eid_uuid = uuid.UUID(entity.execution_id) if len(entity.execution_id) == 36 else uuid.uuid4()

        if existing:
            existing.approval_status = str(entity.approval_status.value if hasattr(entity.approval_status, "value") else entity.approval_status)
            existing.reviewed_by = entity.reviewed_by
            existing.comments = entity.comments
            existing.reviewed_at = entity.reviewed_at
            existing.data_to_review = entity.data_to_review
            existing.state_snapshot = entity.state_snapshot
            return existing

        return WorkflowCheckpointModel(
            id=cid_uuid,
            workflow_id=wf_uuid,
            execution_id=eid_uuid,
            step_id=entity.step_id,
            checkpoint_type=str(entity.checkpoint_type.value if hasattr(entity.checkpoint_type, "value") else entity.checkpoint_type),
            approval_status=str(entity.approval_status.value if hasattr(entity.approval_status, "value") else entity.approval_status),
            title=entity.title,
            description=entity.description,
            data_to_review=entity.data_to_review,
            state_snapshot=entity.state_snapshot,
            assigned_role=entity.assigned_role,
            requested_by=entity.requested_by,
            reviewed_by=entity.reviewed_by,
            comments=entity.comments,
            reviewed_at=entity.reviewed_at,
        )

    async def get_by_id(self, id_: str) -> WorkflowCheckpoint | None:
        try:
            val_uuid = uuid.UUID(id_)
        except ValueError:
            return None
        stmt = select(WorkflowCheckpointModel).where(WorkflowCheckpointModel.id == val_uuid)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_execution(self, execution_id: str) -> list[WorkflowCheckpoint]:
        try:
            eid_uuid = uuid.UUID(execution_id)
        except ValueError:
            return []
        stmt = (
            select(WorkflowCheckpointModel)
            .where(WorkflowCheckpointModel.execution_id == eid_uuid)
            .order_by(WorkflowCheckpointModel.created_at.asc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def list_pending_by_workflow(self, workflow_id: str) -> list[WorkflowCheckpoint]:
        try:
            wf_uuid = uuid.UUID(workflow_id)
        except ValueError:
            return []
        stmt = (
            select(WorkflowCheckpointModel)
            .where(
                WorkflowCheckpointModel.workflow_id == wf_uuid,
                WorkflowCheckpointModel.approval_status == "pending",
            )
            .order_by(WorkflowCheckpointModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
