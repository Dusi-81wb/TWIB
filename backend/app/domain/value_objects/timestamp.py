"""Timestamp value object.

A :class:`Timestamp` wraps a timezone-aware moment normalized to UTC. Naive
datetimes are rejected at construction, so a :class:`Timestamp` instance
always carries an unambiguous instant. The module depends only on the standard
library.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Self

from app.domain.exceptions import InvalidValue
from app.domain.value_object import ValueObject


class Timestamp(ValueObject):
    """An immutable, timezone-aware timestamp normalized to UTC.

    Attributes:
        value: The wrapped moment, always timezone-aware and in UTC.
    """

    value: datetime

    def __init__(self, value: datetime | None = None) -> None:
        """Initialize the timestamp.

        Args:
            value: The moment to store. When omitted, the current UTC time is
                used.

        Raises:
            InvalidValue: When the value is a naive datetime.
        """
        moment = value if value is not None else datetime.now(UTC)
        if moment.tzinfo is None:
            raise InvalidValue("Timestamp must be timezone-aware")
        object.__setattr__(self, "value", moment.astimezone(UTC))

    @classmethod
    def now(cls) -> Self:
        """Create a timestamp for the current UTC moment.

        Returns:
            A timestamp wrapping the current UTC time.
        """
        return cls()

    @classmethod
    def parse(cls, value: str) -> Self:
        """Parse an ISO 8601 string into a timestamp.

        Args:
            value: An ISO 8601 string such as ``2026-08-01T12:00:00Z``.

        Returns:
            A timestamp wrapping the parsed moment.

        Raises:
            InvalidValue: When the string is not a valid ISO 8601 timestamp
                or the parsed moment is naive.
        """
        try:
            moment = datetime.fromisoformat(value)
        except ValueError as exc:
            raise InvalidValue(f"{value!r} is not a valid ISO 8601 timestamp") from exc
        return cls(moment)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because timestamps are immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")

    def __str__(self) -> str:
        """Return the timestamp as an ISO 8601 string."""
        return self.value.isoformat()
