"""Application factory for the TWIB backend.

The FastAPI instance is created lazily through :func:`create_application`
instead of being defined as a global, allowing the application to be
constructed and configured in a controlled and testable way.
"""

from fastapi import FastAPI

from app.api.router import api_router
from app.container import ApplicationContainer
from app.core.constants import SERVICE_NAME, VERSION
from app.core.handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.lifecycle import lifespan


def create_application() -> FastAPI:
    """Create and configure the TWIB FastAPI application.

    Initializes the dependency injection container, resolves the
    application settings through it, configures structured logging,
    registers the global exception handlers, and exposes the container and
    the settings on the application state so every component accesses the
    same configuration and object graph.

    Returns:
        A fully configured FastAPI application instance.
    """
    container = ApplicationContainer()
    settings = container.settings()

    configure_logging(settings)

    application = FastAPI(
        title=SERVICE_NAME,
        version=VERSION,
        lifespan=lifespan,
    )
    application.state.container = container
    application.state.settings = settings

    register_exception_handlers(application)
    application.include_router(api_router)
    return application
