from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import get_logger
from app.infrastructure.cache import close_redis
from app.infrastructure.database import init_db
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
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as err:
        logger.warning(
            "Database initialization encountered an issue",
            error=str(err),
        )

    # Validate OmniRoute settings on startup
    settings = getattr(application.state, "settings", None)
    if settings:
        base_url = settings.omniroute_base_url
        model = settings.default_model
        has_key = bool(settings.omniroute_api_key)
        logger.info(
            "OmniRoute LLM Gateway configured",
            base_url=base_url,
            default_model=model,
            api_key_configured=has_key,
        )

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
