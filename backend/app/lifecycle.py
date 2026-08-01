"""Application lifespan management.

Handles startup and shutdown events. No infrastructure (such as a database)
is initialized during this phase.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown.

    Args:
        application: The FastAPI application instance.

    Yields:
        None once the application is ready to serve requests.
    """
    logger.info("Application Starting")
    logger.info("Application Started")
    try:
        yield
    finally:
        logger.info("Application Shutting Down")
        logger.info("Application Stopped")
