"""Metadata value object.

A :class:`Metadata` wraps an immutable key/value map of strings. The mapping
is copied at construction and never exposed directly, so callers cannot mutate
it after the object is created. The module depends only on the standard
library.
"""

from __future__ import annotations

from app.domain.exceptions import InvalidValue
from app.domain.value_object import ValueObject


class Metadata(ValueObject):
    """An immutable key/value metadata map.

    Keys and values must be strings, and keys must be non-empty. The internal
    mapping is copied at construction; :attr:`value` returns a fresh copy so
    the stored data can never be mutated from outside.

    Attributes:
        value: A copy of the stored key/value mapping.
    """

    _value: dict[str, str]

    def __init__(self, value: dict[str, str] | None = None) -> None:
        """Initialize the metadata.

        Args:
            value: The key/value mapping to store.

        Raises:
            InvalidValue: When a key is not a non-empty string or a value is
                not a string.
        """
        source = value or {}
        snapshot: dict[str, str] = {}
        for key, item in source.items():
            if not isinstance(key, str) or not key:
                raise InvalidValue("Metadata keys must be non-empty strings")
            if not isinstance(item, str):
                raise InvalidValue("Metadata values must be strings")
            snapshot[key] = item
        object.__setattr__(self, "_value", snapshot)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because metadata is immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")

    @property
    def value(self) -> dict[str, str]:
        """Return a copy of the stored key/value mapping."""
        return dict(self._value)

    def __hash__(self) -> int:
        """Return a hash derived from the key/value items."""
        return hash(frozenset(self._value.items()))

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"{type(self).__name__}({self._value!r})"
