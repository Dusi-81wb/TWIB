"""Domain events.

A :class:`DomainEvent` records that something meaningful happened in the
domain. Events are immutable value objects: every occurrence carries a unique
identifier and a UTC timestamp. The domain layer only *records* events; it
never sends emails, updates analytics, or creates notifications.

Base fields are keyword-only, so concrete events can declare their payload
fields without defaults:

    @dataclass(frozen=True, eq=False, repr=False)
    class WorkflowCreated(DomainEvent):
        workflow_id: Identity[uuid.UUID]
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.value_object import ValueObject


@dataclass(frozen=True, kw_only=True, eq=False, repr=False)
class DomainEvent(ValueObject):
    """Base class for all domain events.

    A domain event is an immutable record of something that happened in the
    domain. Every occurrence is uniquely identified by ``event_id`` and
    stamped with the UTC time it was created. Concrete events subclass this
    class and add their domain payload.

    Attributes:
        event_id: Unique identifier of this event occurrence.
        occurred_at: UTC timestamp of when the event occurred.
    """

    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def event_name(self) -> str:
        """Return the machine-readable event name.

        The name defaults to the concrete class name and can be overridden by
        subclasses.
        """
        return type(self).__name__
