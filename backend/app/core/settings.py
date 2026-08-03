"""Application settings loaded from environment variables.

Settings are loaded through Pydantic's ``BaseSettings`` and populated from
the environment and the ``.env`` file. The active environment is selected
with the ``APP_ENV`` environment variable.
"""

from pydantic import Field
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
    secret_key: str = ""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = ""
    redis_url: str = ""
    qdrant_url: str = ""
    ollama_base_url: str = ""
    cors_origins: list[str] = Field(default_factory=list)
