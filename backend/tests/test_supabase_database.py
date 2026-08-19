import pytest
from app.core.settings import ApplicationSettings
from app.infrastructure.database.engine import create_engine

def test_engine_handles_sqlite_fallback():
    settings = ApplicationSettings(database_url="sqlite+aiosqlite:///./test.db")
    engine = create_engine(settings)
    assert "sqlite" in str(engine.url)

def test_engine_normalizes_postgres_url():
    settings = ApplicationSettings(
        database_url="postgresql://postgres:secret@db.supabase.co:5432/postgres"
    )
    engine = create_engine(settings)
    assert engine.url.drivername == "postgresql+asyncpg"

def test_engine_normalizes_postgres_shorthand_url():
    settings = ApplicationSettings(
        database_url="postgres://postgres:secret@db.supabase.co:6543/postgres"
    )
    engine = create_engine(settings)
    assert engine.url.drivername == "postgresql+asyncpg"
