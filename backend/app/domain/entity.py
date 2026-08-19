"""Entities and their identity.

An :class:`Entity` is a domain object defined by its identity rather than its
attributes. Two entities of the same type with the same identity are the same
object regardless of their state, which makes entities safe to mutate. The
:class:`Identity` value object wraps the underlying identifier so an entity's
identity stays stable while the entity changes.

These base classes are framework-independent and depend only on the Python
standard library.
"""

from __future__ import annotations

import uuid
from typing import cast


class Identity[IdentityT: uuid.UUID | str | int]:
    """Stable value type wrapping an entity identifier.

    An identity is immutable and compared by value, so two identities wrapping
    the same underlying value are equal. The wrapped value must be hashable.

    Attributes:
        value: The underlying identifier value.
    """

    _value: IdentityT
    __slots__ = ("_value",)

    def __init__(self, value: IdentityT) -> None:
        """Initialize the identity.

        Args:
            value: The underlying identifier value.
        """
        object.__setattr__(self, "_value", value)

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
    def value(self) -> IdentityT:
        """Return the underlying identifier value."""
        return self._value

    def __eq__(self, other: object) -> bool:
        """Compare identities by value.

        Args:
            other: The object to compare with.

        Returns:
            True when the other object is an identity wrapping the same value.
        """
        if not isinstance(other, Identity):
            return NotImplemented
        return self.value == cast("Identity[IdentityT]", other).value

    def __hash__(self) -> int:
        """Return a hash derived from the wrapped value."""
        return hash(self.value)

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"{type(self).__name__}({self.value!r})"

    def __str__(self) -> str:
        """Return the wrapped value as a string."""
        return str(self.value)


class Entity[EntityID: uuid.UUID | str | int]:
    """Base class for all domain entities.

    An entity is a domain object defined by its identity. Two entities of the
    same type and identity are equal regardless of their state. Concrete
    entities subclass this class, supply an :class:`Identity` to the
    constructor, and add their own mutable state:

    Example:
        class User(Entity[uuid.UUID]):
            def __init__(self, id_: Identity[uuid.UUID], name: str) -> None:
                super().__init__(id_)
                self.name = name
    """

    def __init__(self, id_: Identity[EntityID]) -> None:
        """Initialize the entity with its identity.

        Args:
            id_: The stable identity of the entity.
        """
        self.id = id_

    @property
    def identity(self) -> Identity[EntityID]:
        """Return the entity identity."""
        return self.id

    def __eq__(self, other: object) -> bool:
        """Compare entities by type and identity.

        Args:
            other: The object to compare with.

        Returns:
            True when the other object is an entity of the same type with the
            same identity.
        """
        if not isinstance(other, Entity):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        """Return a hash derived from the entity type and identity."""
        return hash((type(self), self.id))

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        return f"{type(self).__name__}(id={self.id!r})"
