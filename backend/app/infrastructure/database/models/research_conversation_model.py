"""SQLAlchemy models for ResearchAgent persistent conversations and messages."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import JSON, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.base_model import BaseModel


class ResearchConversationModel(BaseModel):
    """ORM model storing persistent research agent conversation threads.

    Attributes:
        user_id: Owner UUID of the user who owns this conversation.
        title: Title of the conversation (auto-generated from first prompt or custom).
        agent_type: Identifier of the agent ('research').
        messages: Cascade-deleted ordered list of conversation messages.
    """

    __tablename__ = "research_conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="New Research",
    )
    agent_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="research",
    )

    messages: Mapped[list[ResearchMessageModel]] = relationship(
        "ResearchMessageModel",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ResearchMessageModel.created_at",
    )

    __table_args__ = (
        Index("ix_research_conversations_user_updated", "user_id", "updated_at"),
    )


class ResearchMessageModel(BaseModel):
    """ORM model storing individual turns (user or assistant) within a conversation.

    Attributes:
        conversation_id: Foreign key linking to parent conversation.
        role: Role of the message sender ('user', 'assistant', 'system').
        content: Text content of the message turn.
        metadata: Additional metadata (provider, model, latency_ms, usage).
    """

    __tablename__ = "research_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("research_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=dict,
    )

    conversation: Mapped[ResearchConversationModel] = relationship(
        "ResearchConversationModel",
        back_populates="messages",
    )

    __table_args__ = (
        Index("ix_research_messages_conv_created", "conversation_id", "created_at"),
    )
