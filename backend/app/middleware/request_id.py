"""Request ID middleware.

Assigns a unique ``UUID4`` to every incoming request, stores it on
``request.state.request_id``, binds it to the structured log context, and
echoes it back to the client through the ``X-Request-ID`` response header.
"""

from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request identifier to every request and response.

    Attributes:
        header_name: Name of the header used to carry the request ID.
    """

    def __init__(self, app, header_name: str = REQUEST_ID_HEADER) -> None:
        """Initialize the middleware.

        Args:
            app: The ASGI application to wrap.
            header_name: Header name used to carry the request ID.
        """
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Generate the request ID and attach it to the response.

        Args:
            request: The incoming request.
            call_next: Callable invoking the next middleware or route.

        Returns:
            The response with the request ID header attached.
        """
        request_id = str(uuid4())
        request.state.request_id = request_id
        structlog.contextvars.bind_contextvars(request_id=request_id)

        try:
            response = await call_next(request)
            response.headers[self.header_name] = request_id
            return response
        finally:
            structlog.contextvars.unbind_contextvars("request_id")
