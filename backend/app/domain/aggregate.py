"""Aggregate roots.

An :class:`AggregateRoot` is an entity that acts as the consistency boundary
for a cluster of entities and value objects. It is the only member of the
cluster that repositories load and save as a whole. Domain events produced
while the aggregate applies its business rules are recorded and exposed to the
outside world exactly once through :meth:`AggregateRoot.pull_domain_events`.
"""

from __future__ import annotations

import uuid

from app.domain.entity import Entity, Identity
from app.domain.event import DomainEvent


class AggregateRoot[EntityID: uuid.UUID | str | int](Entity[EntityID]):
    """Abstract base class for all aggregate roots.

    An aggregate root is an entity that acts as the entry point to a cluster
    of entities and value objects. While its business rules are applied, the
    aggregate records :class:`DomainEvent` instances and hands them to the
    outside world exactly once through :meth:`pull_domain_events`.

    Example:
        class Order(AggregateRoot[uuid.UUID]):
            def __init__(self, id_: Identity[uuid.UUID]) -> None:
                super().__init__(id_)

            def mark_paid(self) -> None:
                self.record_event(OrderPaid(self.id))
    """

    def __init__(self, id_: Identity[EntityID]) -> None:
        """Initialize the aggregate root.

        Args:
            id_: The stable identity of the aggregate root.
        """
        super().__init__(id_)
        self._pending_domain_events: list[DomainEvent] = []

    def record_event(self, event: DomainEvent) -> None:
        """Record a domain event to be published after the operation.

        Args:
            event: The domain event to record.
        """
        self._pending_domain_events.append(event)

    def pull_domain_events(self) -> tuple[DomainEvent, ...]:
        """Return every recorded event and clear the record.

        Returns:
            The recorded events in the order they were recorded.
        """
        events = tuple(self._pending_domain_events)
        self._pending_domain_events.clear()
        return events
