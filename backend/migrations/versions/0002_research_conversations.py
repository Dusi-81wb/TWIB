"""Create research_conversations and research_messages tables.

Revision ID: 0002_research_conversations
Revises: 0001_initial_schema
Create Date: 2026-08-09 10:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_research_conversations"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. research_conversations table
    op.create_table(
        "research_conversations",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
            server_default="New Research",
        ),
        sa.Column(
            "agent_type",
            sa.String(length=50),
            nullable=False,
            server_default="research",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_research_conversations_user_id",
        "research_conversations",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_research_conversations_user_updated",
        "research_conversations",
        ["user_id", "updated_at"],
        unique=False,
    )

    # 2. research_messages table
    op.create_table(
        "research_messages",
        sa.Column("id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("conversation_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["research_conversations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_research_messages_conversation_id",
        "research_messages",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(
        "ix_research_messages_conv_created",
        "research_messages",
        ["conversation_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_research_messages_conv_created", table_name="research_messages")
    op.drop_index(
        "ix_research_messages_conversation_id", table_name="research_messages"
    )
    op.drop_table("research_messages")
    op.drop_index(
        "ix_research_conversations_user_updated", table_name="research_conversations"
    )
    op.drop_index(
        "ix_research_conversations_user_id", table_name="research_conversations"
    )
    op.drop_table("research_conversations")
