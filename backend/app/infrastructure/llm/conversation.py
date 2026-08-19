"""LLM Conversation abstraction.

Provides a provider-independent conversation structure for building and managing
ordered message history in LLM interactions.
"""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.infrastructure.llm.message import ChatMessage, MessageRole


class Conversation(BaseModel):
    """Provider-independent conversation container.

    Attributes:
        id: Unique conversation identifier.
        messages: Ordered sequence of ChatMessage objects.
        metadata: Optional conversation metadata.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique conversation identifier.",
    )
    messages: list[ChatMessage] = Field(
        default_factory=list,
        description="Ordered sequence of conversation messages.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Conversation metadata dictionary.",
    )

    def add_message(
        self,
        role: MessageRole | str,
        content: str,
        name: str | None = None,
        tool_call_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ChatMessage:
        """Append a new message to the conversation.

        Args:
            role: Message role (system, user, assistant, tool).
            content: Text content of the message.
            name: Optional author name.
            tool_call_id: Optional tool call reference ID.
            metadata: Optional message metadata.

        Returns:
            The created ChatMessage object.
        """
        msg = ChatMessage(
            role=role,
            content=content,
            name=name,
            tool_call_id=tool_call_id,
            metadata=metadata or {},
        )
        self.messages.append(msg)
        return msg

    def add_system_message(self, content: str) -> ChatMessage:
        """Append a system message to the conversation.

        Args:
            content: System prompt content.

        Returns:
            The created ChatMessage object.
        """
        return self.add_message(MessageRole.SYSTEM, content)

    def add_user_message(self, content: str, name: str | None = None) -> ChatMessage:
        """Append a user message to the conversation.

        Args:
            content: User prompt content.
            name: Optional user display name.

        Returns:
            The created ChatMessage object.
        """
        return self.add_message(MessageRole.USER, content, name=name)

    def add_assistant_message(self, content: str) -> ChatMessage:
        """Append an assistant response message to the conversation.

        Args:
            content: Assistant response text.

        Returns:
            The created ChatMessage object.
        """
        return self.add_message(MessageRole.ASSISTANT, content)

    def add_tool_message(
        self,
        content: str,
        tool_call_id: str,
    ) -> ChatMessage:
        """Append a tool execution result message to the conversation.

        Args:
            content: Tool result content.
            tool_call_id: ID of the tool call being answered.

        Returns:
            The created ChatMessage object.
        """
        return self.add_message(MessageRole.TOOL, content, tool_call_id=tool_call_id)

    def clear(self) -> None:
        """Clear all messages from the conversation history."""
        self.messages.clear()

    @property
    def system_prompt(self) -> str | None:
        """Return content of the initial system message, if any.

        Returns:
            System prompt string or None.
        """
        for msg in self.messages:
            r = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            if r == MessageRole.SYSTEM.value:
                return msg.content
        return None

    @property
    def last_message(self) -> ChatMessage | None:
        """Return the most recent message in the conversation.

        Returns:
            Last ChatMessage or None if empty.
        """
        return self.messages[-1] if self.messages else None

    def __len__(self) -> int:
        """Return the total number of messages in the conversation."""
        return len(self.messages)

    def to_dict(self) -> dict[str, Any]:
        """Serialize conversation to dictionary format.

        Returns:
            Dictionary representation of the conversation.
        """
        return self.model_dump()

    def to_json(self) -> str:
        """Serialize conversation to JSON string.

        Returns:
            JSON string representation.
        """
        return self.model_dump_json()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Conversation:
        """Deserialize conversation from dictionary format.

        Args:
            data: Dictionary representation.

        Returns:
            Deserialized Conversation instance.
        """
        return cls.model_validate(data)

    @classmethod
    def from_json(cls, json_str: str) -> Conversation:
        """Deserialize conversation from JSON string.

        Args:
            json_str: JSON string representation.

        Returns:
            Deserialized Conversation instance.
        """
        return cls.model_validate_json(json_str)
