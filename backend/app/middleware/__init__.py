"""Middleware infrastructure for the TWIB backend.

The middleware package owns request and response cross-cutting concerns.
Every middleware is registered centrally through
:func:`app.middleware.registration.register_middlewares`, which the
application factory calls exactly once.
"""

from app.middleware.cors import configure_cors
from app.middleware.registration import register_middlewares
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

__all__ = [
    "RequestIDMiddleware",
    "SecurityHeadersMiddleware",
    "configure_cors",
    "register_middlewares",
]
