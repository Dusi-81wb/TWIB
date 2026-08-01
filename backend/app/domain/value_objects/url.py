"""URL value object.

A :class:`Url` wraps a validated http or https URL. The value is checked for a
supported scheme and a non-empty host at construction, so a :class:`Url`
instance always holds a usable absolute URL. The module depends only on the
standard library.
"""

from __future__ import annotations

from urllib.parse import urlparse

from app.domain.exceptions import InvalidValue
from app.domain.value_object import ValueObject

_ALLOWED_SCHEMES = frozenset({"http", "https"})


class Url(ValueObject):
    """An immutable, validated http or https URL.

    Attributes:
        value: The URL as provided (trimmed).
    """

    value: str

    def __init__(self, value: str) -> None:
        """Initialize the URL.

        Args:
            value: The URL to validate and store.

        Raises:
            InvalidValue: When the URL is empty, has an unsupported scheme,
                or has no host.
        """
        normalized = value.strip()
        if not normalized:
            raise InvalidValue("URL cannot be empty")
        parsed = urlparse(normalized)
        if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
            raise InvalidValue(f"{value!r} must be an http or https URL")
        if not parsed.netloc:
            raise InvalidValue(f"{value!r} is not a valid URL")
        object.__setattr__(self, "value", normalized)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because URLs are immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")

    def __str__(self) -> str:
        """Return the URL."""
        return self.value
