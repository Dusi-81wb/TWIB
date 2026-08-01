"""Central middleware registration.

The application factory calls :func:`register_middlewares` only; middleware
is never added directly inside ``app/application.py``.
"""

from fastapi import FastAPI

from app.core.settings import ApplicationSettings
from app.middleware.cors import configure_cors
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware


def register_middlewares(
    application: FastAPI,
    settings: ApplicationSettings,
) -> None:
    """Register every middleware on a FastAPI application.

    Middleware added later is placed further out in the request/response
    stack, so the effective order is security headers, request ID, then
    CORS.

    Args:
        application: The FastAPI application to configure.
        settings: Application settings used to configure CORS.
    """
    configure_cors(application, settings)
    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(SecurityHeadersMiddleware)
