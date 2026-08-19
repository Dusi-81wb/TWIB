"""Repository for persisting and managing ResearchAgent conversation threads."""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.models.research_conversation_model import (
    ResearchConversationModel,
    ResearchMessageModel,
)


def generate_smart_title(prompt: str) -> str:
    """Generate a clean, intelligent conversation title from the first user prompt."""
    cleaned = prompt.strip()
    prefix_pattern = (
        r"^(explain|what is|what are|how to|how does|tell me about|"
        r"can you|describe|compare)\s+"
    )
    cleaned = re.sub(prefix_pattern, "", cleaned, flags=re.IGNORECASE).strip()
    if not cleaned:
        cleaned = prompt.strip()

    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]

    if len(cleaned) > 50:
        cleaned = cleaned[:47].rstrip() + "..."

    return cleaned or "New Research"


class SQLAlchemyResearchConversationRepository:
    """SQLAlchemy 2.0 repository for Research Conversations and Message turns."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository bound to an AsyncSession.

        Args:
            session: Active AsyncSession instance.
        """
        self._session = session

    async def create_conversation(
        self,
        *,
        user_id: uuid.UUID,
        title: str = "New Research",
        agent_type: str = "research",
    ) -> ResearchConversationModel:
        """Create and persist a new conversation thread."""
        conversation = ResearchConversationModel(
            user_id=user_id,
            title=title,
            agent_type=agent_type,
        )
        self._session.add(conversation)
        await self._session.flush()
        return conversation

    async def get_conversation(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ResearchConversationModel | None:
        """Fetch conversation by ID verifying user ownership."""
        stmt = (
            select(ResearchConversationModel)
            .options(selectinload(ResearchConversationModel.messages))
            .where(
                ResearchConversationModel.id == conversation_id,
                ResearchConversationModel.user_id == user_id,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_conversations_by_user(
        self,
        user_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ResearchConversationModel]:
        """List persistent conversations for user ordered by last updated timestamp."""
        stmt = (
            select(ResearchConversationModel)
            .options(selectinload(ResearchConversationModel.messages))
            .where(ResearchConversationModel.user_id == user_id)
            .order_by(ResearchConversationModel.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_title(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
    ) -> bool:
        """Update conversation title if owned by user."""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False
        conversation.title = title
        conversation.updated_at = datetime.now(UTC)
        await self._session.flush()
        return True

    async def delete_conversation(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete conversation and all cascaded messages if owned by user."""
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False
        await self._session.delete(conversation)
        await self._session.flush()
        return True

    async def add_message(
        self,
        *,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        metadata_json: dict[str, Any] | None = None,
    ) -> ResearchMessageModel:
        """Append a message turn to an existing conversation and touch updated_at."""
        message = ResearchMessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata_json=metadata_json or {},
        )
        self._session.add(message)

        stmt = select(ResearchConversationModel).where(
            ResearchConversationModel.id == conversation_id
        )
        result = await self._session.execute(stmt)
        conv = result.scalar_one_or_none()
        if conv:
            conv.updated_at = datetime.now(UTC)

        await self._session.flush()
        return message
