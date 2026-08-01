"""Singleton configuration loader.

The application loads settings from exactly one location through
:func:`get_settings`. The cached result is immutable once created, and no
mutable global state is introduced.
"""

from functools import lru_cache

from app.core.settings import ApplicationSettings


@lru_cache(maxsize=1)
def get_settings() -> ApplicationSettings:
    """Return the cached application settings instance.

    The first call parses the environment and the ``.env`` file. Subsequent
    calls return the same immutable instance, so every part of the
    application shares one source of truth.

    Returns:
        The singleton ``ApplicationSettings`` instance.
    """
    return ApplicationSettings()
