"""Repository for persisting and retrieving ResearchExecution entities."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.research_execution_model import (
    ResearchExecutionModel,
)


class SQLAlchemyResearchExecutionRepository:
    """SQLAlchemy 2.0 repository for ResearchExecution records."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository bound to an AsyncSession.

        Args:
            session: Active AsyncSession instance.
        """
        self._session = session

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        prompt: str,
        response: str,
        provider: str = "omniroute",
        model: str = "best-free",
        latency_ms: float = 0.0,
        usage: dict[str, Any] | None = None,
    ) -> ResearchExecutionModel:
        """Persist a new ResearchExecution record.

        Args:
            user_id: Owner user UUID.
            prompt: User research query prompt.
            response: LLM Gateway response answer string.
            provider: LLM provider name (e.g. 'omniroute').
            model: LLM model identifier.
            latency_ms: Execution duration in ms.
            usage: Token usage metrics dict.

        Returns:
            The created ResearchExecutionModel instance.
        """
        record = ResearchExecutionModel(
            user_id=user_id,
            prompt=prompt,
            response=response,
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            usage=usage or {},
        )
        self._session.add(record)
        await self._session.flush()
        return record

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ResearchExecutionModel]:
        """Fetch latest ResearchExecution records for a specific user.

        Args:
            user_id: Owner user UUID.
            limit: Maximum records to return.
            offset: Number of records to skip.

        Returns:
            List of ResearchExecutionModel instances ordered by created_at descending.
        """
        stmt = (
            select(ResearchExecutionModel)
            .where(ResearchExecutionModel.user_id == user_id)
            .order_by(ResearchExecutionModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
