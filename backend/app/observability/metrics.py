"""Metrics interfaces.

Defines the contracts for the metrics instruments used by the application.
Only the interfaces are declared here; a concrete backend (for example
Prometheus or OpenTelemetry) will implement them in a later phase.
"""

from contextlib import AbstractContextManager
from typing import Protocol


class Counter(Protocol):
    """A monotonically increasing counter."""

    def add(self, amount: float = 1) -> None:
        """Increase the counter by the given amount.

        Args:
            amount: Amount to add; defaults to one.
        """
        ...


class Gauge(Protocol):
    """A value that can go up and down."""

    def set(self, value: float) -> None:
        """Set the gauge to an absolute value.

        Args:
            value: Value to set.
        """
        ...

    def inc(self) -> None:
        """Increase the gauge by one."""
        ...

    def dec(self) -> None:
        """Decrease the gauge by one."""
        ...


class Histogram(Protocol):
    """A distribution of observed values."""

    def observe(self, value: float) -> None:
        """Record a single observation.

        Args:
            value: Observed value to add to the distribution.
        """
        ...


class Timer(Protocol):
    """A context manager that records elapsed time."""

    def time(self) -> AbstractContextManager[None]:
        """Record the elapsed time of the enclosed block."""
        ...
