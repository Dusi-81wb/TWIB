"""Value objects.

A :class:`ValueObject` is an immutable domain object defined entirely by its
attributes. Two value objects of the same type with the same attribute values
are equal and interchangeable. Value objects have no identity, so they can be
shared and cached freely.

Subclasses are expected to be declared as immutable dataclasses so equality,
hashing, and representation are inherited from this class:

    @dataclass(frozen=True, eq=False)
    class Email(ValueObject):
        value: str

All attribute values must be hashable.
"""

from __future__ import annotations


class ValueObject:
    """Base class for all value objects.

    Value objects are immutable and compared by value. Two value objects of
    the same type with the same attribute values are equal, so they can be
    shared and cached freely. Subclasses should be declared as frozen
    dataclasses with ``eq=False`` (and optionally ``repr=False``) so equality,
    hashing, and representation are inherited from this class.
    """

    def __eq__(self, other: object) -> bool:
        """Compare value objects by type and attributes.

        Args:
            other: The object to compare with.

        Returns:
            True when the other object is a value object of the same type with
            identical attribute values.
        """
        if not isinstance(other, ValueObject) or type(self) is not type(other):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """Return a hash derived from the attribute values."""
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the attribute values."""
        fields = ", ".join(f"{name}={value!r}" for name, value in self.__dict__.items())
        return f"{type(self).__name__}({fields})"
