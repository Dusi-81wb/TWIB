"""Application settings loaded from environment variables.

Settings are loaded through Pydantic's ``BaseSettings`` and populated from
the environment and the ``.env`` file. The active environment is selected
with the ``APP_ENV`` environment variable.
"""

import json
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import API_PREFIX, SERVICE_NAME, VERSION
from app.core.environments import Environment


class ApplicationSettings(BaseSettings):
    """Typed application configuration.

    Attributes:
        app_name: Public name of the application.
        app_version: Version of the application.
        app_env: Active environment (development, testing, or production).
        debug: Enable debug mode.
        host: Host the application binds to.
        port: Port the application listens on.
        api_prefix: URL prefix for API routes.
        log_level: Logging level used by the application.
        secret_key: Secret used for signing and cryptography.
        database_url: Connection string for the PostgreSQL database.
        redis_url: Connection string for the Redis cache.
        qdrant_url: Base URL for the Qdrant vector database.
        ollama_base_url: Base URL of the Ollama LLM server.
        cors_origins: Allowed cross-origin request origins.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = SERVICE_NAME
    app_version: str = VERSION
    app_env: Environment = Environment.DEVELOPMENT
    debug: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    api_prefix: str = API_PREFIX
    log_level: str = "INFO"
    secret_key: str = "twib-development-secret-key-32-chars-minimum!"  # noqa: S105
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite+aiosqlite:///./twib.db"
    redis_url: str = ""
    qdrant_url: str = ""
    ollama_base_url: str = ""
    openai_api_key: str = ""
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_database_url(cls, v: Any) -> str:
        """Fallback to sqlite+aiosqlite when database_url is empty."""
        if not v or not isinstance(v, str) or not v.strip():
            return "sqlite+aiosqlite:///./twib.db"
        return v.strip()

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from json string, comma list, or list."""
        default_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
        if not v:
            return default_origins
        if isinstance(v, str):
            v_str = v.strip()
            if not v_str:
                return default_origins
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    parsed = json.loads(v_str)
                    if isinstance(parsed, list):
                        res = [str(item).strip() for item in parsed if item]
                        return res if res else default_origins
                except json.JSONDecodeError:
                    pass
            res = [item.strip() for item in v_str.split(",") if item.strip()]
            return res if res else default_origins
        if isinstance(v, list):
            res = [str(item).strip() for item in v if item]
            return res if res else default_origins
        return default_origins
