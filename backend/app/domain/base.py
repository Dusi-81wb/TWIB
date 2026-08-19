"""Reusable abstract base classes for the domain layer.

This module aggregates the foundational, framework-independent base classes of
the domain layer so they can be imported from a single location:

    from app.domain.base import AggregateRoot, Entity, Identity

The canonical definitions live in their dedicated modules (:mod:`app.domain.entity`,
:mod:`app.domain.aggregate`, :mod:`app.domain.value_object`, and
:mod:`app.domain.event`).
"""

from __future__ import annotations

from app.domain.aggregate import AggregateRoot
from app.domain.entity import Entity, Identity
from app.domain.event import DomainEvent
from app.domain.value_object import ValueObject

__all__ = [
    "AggregateRoot",
    "DomainEvent",
    "Entity",
    "Identity",
    "ValueObject",
]
