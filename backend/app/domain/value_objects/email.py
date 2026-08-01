"""Email address value object.

An :class:`Email` wraps a validated email address. The address is normalized
(lowercased, surrounding whitespace removed) and validated at construction, so
an :class:`Email` instance always holds a syntactically valid address. The
module depends only on the standard library.
"""

from __future__ import annotations

import re

from app.domain.exceptions import InvalidValue
from app.domain.value_object import ValueObject

_EMAIL_PATTERN = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$")


class Email(ValueObject):
    """An immutable, validated email address.

    Attributes:
        value: The normalized email address (lowercase, no surrounding
            whitespace).
    """

    value: str

    def __init__(self, value: str) -> None:
        """Initialize the email.

        Args:
            value: The email address to validate and store.

        Raises:
            InvalidValue: When the address is empty or syntactically invalid.
        """
        normalized = value.strip().lower()
        if not normalized:
            raise InvalidValue("Email address cannot be empty")
        if _EMAIL_PATTERN.fullmatch(normalized) is None:
            raise InvalidValue(f"{value!r} is not a valid email address")
        object.__setattr__(self, "value", normalized)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because emails are immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")

    def __str__(self) -> str:
        """Return the email address."""
        return self.value
