"""Security headers middleware.

Adds security-relevant response headers to every response. Content Security
Policy is intentionally deferred to a later phase.
"""

from typing import ClassVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach security headers to every response.

    Attributes:
        headers: Header name/value pairs applied to every response.
    """

    headers: ClassVar[dict[str, str]] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "X-XSS-Protection": "1; mode=block",
    }

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Apply the security headers to the generated response.

        Args:
            request: The incoming request.
            call_next: Callable invoking the next middleware or route.

        Returns:
            The response with the security headers attached.
        """
        response = await call_next(request)
        response.headers.update(self.headers)
        return response
