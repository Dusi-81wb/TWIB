"""Workspace settings domain object.

A :class:`WorkspaceSettings` is an immutable configuration object for a
workspace: timezone, default language, visibility, AI model preference,
execution limits, knowledge-base toggle, and experimental-features toggle. It
is a domain object built from validated primitive values; it carries no
behaviour beyond its own validation. The :class:`WorkspaceVisibility`
enumeration is also defined here because it belongs to the settings concept.

No infrastructure (databases, caches, LLM clients) is involved.
"""

from __future__ import annotations

from enum import StrEnum

from app.domain.exceptions import InvalidValue
from app.domain.value_object import ValueObject


class WorkspaceVisibility(StrEnum):
    """The visibility of a workspace.

    Members:
        PRIVATE: Only workspace members can see it.
        ORGANIZATION: Members of the parent organization can see it.
        PUBLIC: Anyone with the link can see it.
    """

    PRIVATE = "private"
    ORGANIZATION = "organization"
    PUBLIC = "public"


class WorkspaceSettings(ValueObject):
    """An immutable configuration object for a workspace.

    All settings are validated at construction; invalid values raise
    :class:`~app.domain.exceptions.InvalidValue`. The object is compared and
    hashed by value, so two settings objects with the same values are equal.

    Attributes:
        timezone: The workspace timezone (for example ``UTC``).
        default_language: The default language (for example ``en``).
        visibility: The workspace visibility.
        ai_model_preference: The preferred AI model routing hint.
        execution_limits: The maximum number of concurrent executions.
        knowledge_base_enabled: Whether the knowledge base is enabled.
        experimental_features: Whether experimental features are enabled.
    """

    timezone: str
    default_language: str
    visibility: WorkspaceVisibility
    ai_model_preference: str
    execution_limits: int
    knowledge_base_enabled: bool
    experimental_features: bool

    def __init__(
        self,
        timezone: str = "UTC",
        default_language: str = "en",
        visibility: WorkspaceVisibility = WorkspaceVisibility.PRIVATE,
        ai_model_preference: str = "auto",
        execution_limits: int = 5,
        knowledge_base_enabled: bool = False,
        experimental_features: bool = False,
    ) -> None:
        """Initialize the settings.

        Args:
            timezone: The workspace timezone (defaults to ``UTC``).
            default_language: The default language (defaults to ``en``).
            visibility: The workspace visibility (defaults to PRIVATE).
            ai_model_preference: The preferred AI model routing hint
                (defaults to ``auto``).
            execution_limits: The maximum number of concurrent executions
                (defaults to 5).
            knowledge_base_enabled: Whether the knowledge base is enabled
                (defaults to False).
            experimental_features: Whether experimental features are enabled
                (defaults to False).

        Raises:
            InvalidValue: When a non-empty string is empty or the execution
                limit is negative.
        """
        if not timezone.strip():
            raise InvalidValue("Timezone cannot be empty")
        if not default_language.strip():
            raise InvalidValue("Default language cannot be empty")
        if not ai_model_preference.strip():
            raise InvalidValue("AI model preference cannot be empty")
        if execution_limits < 0:
            raise InvalidValue("Execution limits cannot be negative")
        object.__setattr__(self, "timezone", timezone.strip())
        object.__setattr__(self, "default_language", default_language.strip())
        object.__setattr__(self, "visibility", visibility)
        object.__setattr__(self, "ai_model_preference", ai_model_preference.strip())
        object.__setattr__(self, "execution_limits", execution_limits)
        object.__setattr__(self, "knowledge_base_enabled", knowledge_base_enabled)
        object.__setattr__(self, "experimental_features", experimental_features)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because settings are immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return (
            f"{type(self).__name__}("
            f"timezone={self.timezone!r}, "
            f"default_language={self.default_language!r}, "
            f"visibility={self.visibility!r}, "
            f"ai_model_preference={self.ai_model_preference!r}, "
            f"execution_limits={self.execution_limits!r}, "
            f"knowledge_base_enabled={self.knowledge_base_enabled!r}, "
            f"experimental_features={self.experimental_features!r})"
        )
