"""UUID-based identity value object.

A :class:`UuidIdentity` is an immutable, value-comparable wrapper around a
:class:`uuid.UUID`. It is the dedicated identity type for domain entities and
can be generated or parsed from its canonical string form. The module depends
only on the standard library, so it stays framework-independent.
"""

from __future__ import annotations

import uuid
from typing import Self

from app.domain.exceptions import InvalidValue


class UuidIdentity:
    """Immutable value type wrapping a UUID identifier.

    Two identities wrapping the same UUID are equal and interchangeable. The
    wrapped value cannot be mutated after construction.

    Attributes:
        value: The underlying :class:`uuid.UUID`.
    """

    _value: uuid.UUID
    __slots__ = ("_value",)

    def __init__(self, value: uuid.UUID) -> None:
        """Initialize the identity.

        Args:
            value: The underlying UUID identifier.
        """
        object.__setattr__(self, "_value", value)

    @classmethod
    def generate(cls) -> Self:
        """Create a new identity with a fresh random UUID4.

        Returns:
            A new identity wrapping a generated UUID4.
        """
        return cls(uuid.uuid4())

    @classmethod
    def parse(cls, value: str) -> Self:
        """Parse a canonical UUID string into an identity.

        Args:
            value: A string in the canonical ``8-4-4-4-12`` hexadecimal
                format.

        Returns:
            An identity wrapping the parsed UUID.

        Raises:
            InvalidValue: When the string is not a valid UUID.
        """
        try:
            parsed = uuid.UUID(value)
        except (ValueError, AttributeError) as exc:
            raise InvalidValue(f"{value!r} is not a valid UUID") from exc
        return cls(parsed)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because identities are immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")

    @property
    def value(self) -> uuid.UUID:
        """Return the underlying UUID."""
        return self._value

    def __eq__(self, other: object) -> bool:
        """Compare identities by value.

        Args:
            other: The object to compare with.

        Returns:
            True when the other object is a UUID identity wrapping the same
            UUID.
        """
        if not isinstance(other, UuidIdentity):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        """Return a hash derived from the wrapped UUID."""
        return hash(self.value)

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"{type(self).__name__}({self.value!r})"

    def __str__(self) -> str:
        """Return the canonical UUID string."""
        return str(self.value)
