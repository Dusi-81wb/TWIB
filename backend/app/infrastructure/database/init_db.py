"""Database initialization helper.

Ensures that database tables exist on application startup.
"""

from __future__ import annotations

import app.infrastructure.database.models  # noqa: F401
from app.core.logging import get_logger
from app.infrastructure.database.base import Base
from app.infrastructure.database.engine import get_engine

logger = get_logger(__name__)


async def init_db() -> None:
    """Initialize database tables asynchronously on application startup."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema initialized successfully")
