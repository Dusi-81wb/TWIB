"""Observability middleware.

Builds a :class:`RequestContext` for every request from the request state
and stores it on ``request.state.context`` so downstream middleware and
route handlers can access the correlation identifiers without recomputing
them.
"""

from datetime import UTC, datetime
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.observability.request_context import RequestContext


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Attach a request context to every request.

    The context is derived from the request ID already assigned by the
    request ID middleware and a fresh correlation ID.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Build the request context and store it on the request state.

        Args:
            request: The incoming request.
            call_next: Callable invoking the next middleware or route.

        Returns:
            The response produced downstream.
        """
        request_id = getattr(request.state, "request_id", None) or str(uuid4())
        request.state.context = RequestContext(
            request_id=request_id,
            timestamp=datetime.now(UTC),
            correlation_id=str(uuid4()),
        )

        return await call_next(request)
