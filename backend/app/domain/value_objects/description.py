"""Description value object.

A :class:`Description` wraps a validated free-text description. The value is
trimmed and checked for length at construction, so a :class:`Description`
instance always holds a usable description. Unlike :class:`Name`, an empty
description is allowed because descriptions are optional. The module depends
only on the standard library.
"""

from __future__ import annotations

from app.domain.exceptions import InvalidValue
from app.domain.value_object import ValueObject

_MAX_DESCRIPTION_LENGTH = 500


class Description(ValueObject):
    """An immutable, validated free-text description.

    Attributes:
        value: The normalized description (trimmed, within length limits).
    """

    value: str

    def __init__(self, value: str = "") -> None:
        """Initialize the description.

        Args:
            value: The description to validate and store (defaults to empty).

        Raises:
            InvalidValue: When the description is too long.
        """
        normalized = value.strip()
        if len(normalized) > _MAX_DESCRIPTION_LENGTH:
            raise InvalidValue(
                f"Description cannot exceed {_MAX_DESCRIPTION_LENGTH} characters"
            )
        object.__setattr__(self, "value", normalized)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because descriptions are immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")

    def __str__(self) -> str:
        """Return the description."""
        return self.value
