"""TWIB domain layer.

The domain layer contains the enterprise business rules of the platform. It is
pure Python with no framework, database, or HTTP dependencies, so it can be
reused by every outer layer without coupling.

This package exports the domain primitives (:class:`Entity`,
:class:`AggregateRoot`, :class:`ValueObject`, :class:`DomainEvent`, and
:class:`Identity`) together with the domain exception hierarchy
(:class:`DomainException` and its subclasses).
"""

from __future__ import annotations

from app.domain.base import (
    AggregateRoot,
    DomainEvent,
    Entity,
    Identity,
    ValueObject,
)
from app.domain.exceptions import (
    BusinessRuleViolation,
    DomainException,
    EntityNotFound,
    InvalidOperation,
)

__all__ = [
    "AggregateRoot",
    "BusinessRuleViolation",
    "DomainEvent",
    "DomainException",
    "Entity",
    "EntityNotFound",
    "Identity",
    "InvalidOperation",
    "ValueObject",
]
