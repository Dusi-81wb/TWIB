"""Observability primitives for the TWIB backend.

This package defines the request-scoped context object and the interfaces
for metrics and tracing. The concrete adapters (Prometheus, OpenTelemetry,
Jaeger) are intentionally not implemented in this phase; they will implement
the protocols defined in :mod:`app.observability.metrics` and
:mod:`app.observability.tracing` in a later phase.
"""

from app.observability.events import EventType
from app.observability.metrics import Counter, Gauge, Histogram, Timer
from app.observability.request_context import RequestContext
from app.observability.tracing import Span, Tracer

__all__ = [
    "Counter",
    "EventType",
    "Gauge",
    "Histogram",
    "RequestContext",
    "Span",
    "Timer",
    "Tracer",
]
