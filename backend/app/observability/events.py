"""Application event definitions.

Events are described here so producers and consumers agree on their names
before any publishing infrastructure exists. Events are intentionally not
published in this phase; an event bus will be added in a later phase.
"""

from enum import StrEnum


class EventType(StrEnum):
    """Names of the application events.

    The string values are the stable identifiers used when an event is
    eventually published. No event is emitted from this module.
    """

    APPLICATION_STARTED = "application.started"
    APPLICATION_STOPPED = "application.stopped"
    REQUEST_RECEIVED = "request.received"
    REQUEST_COMPLETED = "request.completed"
    HEALTH_CHECKED = "health.checked"
