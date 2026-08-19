"""Shared pytest fixtures for the TWIB backend test suite."""

from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.application import create_application
from app.infrastructure.database.session import session_scope


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Provide a configured FastAPI test client.

    The client is built through the application factory and entered as a
    context manager so the FastAPI lifespan handlers run for every test.
    Tests request this fixture instead of constructing their own client,
    which keeps application setup in one place.

    Yields:
        A ready-to-use ``TestClient`` bound to a running application.
    """
    with TestClient(create_application()) as test_client:
        yield test_client


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Provide a request-scoped AsyncSession for testing database operations."""
    async with session_scope() as session:
        yield session
