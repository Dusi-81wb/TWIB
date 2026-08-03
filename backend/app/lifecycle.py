from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import get_logger
from app.infrastructure.cache import close_redis
from app.infrastructure.vector import close_vector_store

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
        try:
            await close_redis()
        except Exception as err:
            logger.warning("Error closing Redis connection on shutdown", error=str(err))
        try:
            await close_vector_store()
        except Exception as err:
            logger.warning(
                "Error closing Qdrant vector store connection on shutdown",
                error=str(err),
            )
        logger.info("Application Stopped")
