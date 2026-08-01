"""Version value object.

A :class:`Version` wraps a semantic version composed of non-negative
``major``, ``minor``, and ``patch`` components. It validates at construction
and can be parsed from its canonical ``major.minor.patch`` string form. The
module depends only on the standard library.
"""

from __future__ import annotations

from typing import Self

from app.domain.exceptions import InvalidValue
from app.domain.value_object import ValueObject


class Version(ValueObject):
    """An immutable, validated semantic version.

    Attributes:
        major: The major version component.
        minor: The minor version component.
        patch: The patch version component.
    """

    major: int
    minor: int
    patch: int

    def __init__(self, major: int, minor: int = 0, patch: int = 0) -> None:
        """Initialize the version.

        Args:
            major: The major version component.
            minor: The minor version component.
            patch: The patch version component.

        Raises:
            InvalidValue: When any component is negative.
        """
        if major < 0 or minor < 0 or patch < 0:
            raise InvalidValue("Version components cannot be negative")
        object.__setattr__(self, "major", major)
        object.__setattr__(self, "minor", minor)
        object.__setattr__(self, "patch", patch)

    @classmethod
    def parse(cls, value: str) -> Self:
        """Parse a ``major.minor.patch`` string into a version.

        Args:
            value: A version string such as ``1.2.3``.

        Returns:
            A version with the parsed components.

        Raises:
            InvalidValue: When the string is not a three-part dotted numeric
                version.
        """
        parts = value.strip().split(".")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            raise InvalidValue(f"{value!r} is not a valid major.minor.patch version")
        major, minor, patch = (int(part) for part in parts)
        return cls(major, minor, patch)

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Args:
            name: The attribute being assigned.
            value: The value being assigned.

        Raises:
            TypeError: Always raised because versions are immutable.
        """
        raise TypeError(f"{type(self).__name__} instances are immutable")

    def __str__(self) -> str:
        """Return the version as ``major.minor.patch``."""
        return f"{self.major}.{self.minor}.{self.patch}"
