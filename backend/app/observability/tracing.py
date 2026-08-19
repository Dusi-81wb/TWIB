"""Tracing interfaces.

Defines the contracts for spans and tracers. Only the interfaces are
declared here; a concrete backend (for example OpenTelemetry or Jaeger)
will implement them in a later phase.
"""

from contextlib import AbstractContextManager
from typing import Protocol


class Span(Protocol):
    """A single unit of traced work."""

    def set_attribute(self, key: str, value: object) -> None:
        """Attach an attribute to the span.

        Args:
            key: Attribute name.
            value: Attribute value.
        """
        ...

    def end(self) -> None:
        """Finish the span."""
        ...


class Tracer(Protocol):
    """Creates and manages spans."""

    def start_span(self, name: str) -> Span:
        """Start a new span.

        Args:
            name: Name of the span.

        Returns:
            The started span.
        """
        ...

    def span(self, name: str) -> AbstractContextManager[Span]:
        """Create a span to use as a context manager.

        Args:
            name: Name of the span.

        Returns:
            A context manager that starts and ends the span.
        """
        ...
