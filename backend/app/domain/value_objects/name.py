"""Name value object.

A :class:`Name` wraps a validated display name. The value is trimmed and
checked for emptiness and length at construction, so a :class:`Name` instance
always holds a usable display name. The module depends only on the standard
library.
"""

from __future__ import annotations

from app.domain.exceptions import InvalidValue
from app.domain.value_object import ValueObject

_MAX_NAME_LENGTH = 120


class Name(ValueObject):
    """An immutable, validated display name.

    Attributes:
        value: The normalized name (trimmed, non-empty, within length limits).
    """

    value: str

    def __init__(self, value: str) -> None:
        """Initialize the name.

        Args:
            value: The display name to validate and store.

        Raises:
            InvalidValue: When the name is empty or too long.
        """
        normalized = value.strip()
        if not normalized:
            raise InvalidValue("Name cannot be empty")
        if len(normalized) > _MAX_NAME_LENGTH:
            raise InvalidValue(f"Name cannot exceed {_MAX_NAME_LENGTH} characters")
        object.__setattr__(self, "value", normalized)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because names are immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")

    def __str__(self) -> str:
        """Return the name."""
        return self.value
