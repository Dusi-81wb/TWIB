"""Slug value object.

A :class:`Slug` wraps a validated URL- and database-friendly slug. The value
is normalized (lowercased, trimmed) and checked against a strict character
pattern at construction. The module depends only on the standard library.
"""

from __future__ import annotations

import re

from app.domain.exceptions import InvalidValue
from app.domain.value_object import ValueObject

_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class Slug(ValueObject):
    """An immutable, validated slug.

    A slug consists of lowercase letters, digits, and hyphens. Hyphens may not
    lead, trail, or repeat, so slugs are URL-safe and unambiguous.

    Attributes:
        value: The normalized slug (lowercase, trimmed).
    """

    value: str

    def __init__(self, value: str) -> None:
        """Initialize the slug.

        Args:
            value: The slug to validate and store.

        Raises:
            InvalidValue: When the slug is empty or does not match the slug
                character pattern.
        """
        normalized = value.strip().lower()
        if not normalized:
            raise InvalidValue("Slug cannot be empty")
        if _SLUG_PATTERN.fullmatch(normalized) is None:
            raise InvalidValue(f"{value!r} is not a valid slug")
        object.__setattr__(self, "value", normalized)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because slugs are immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")

    def __str__(self) -> str:
        """Return the slug."""
        return self.value
