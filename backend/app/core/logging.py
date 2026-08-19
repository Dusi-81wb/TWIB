"""Structured logging configuration using structlog.

Provides :func:`configure_logging` to install the application-wide logging
pipeline and :func:`get_logger` to obtain named, bound loggers.

The output format depends on the active environment:

- Development renders readable, colorized key/value lines to the console.
- Production renders one JSON object per line, suitable for log
  aggregators.

The active log level is read from ``LOG_LEVEL`` in the application
settings.
"""

import logging
from typing import Any, cast

import structlog

from app.core.config import get_settings
from app.core.environments import Environment
from app.core.settings import ApplicationSettings


def _resolve_level(level_name: str) -> int:
    """Convert a log level name into its numeric logging level.

    Args:
        level_name: A level name such as ``INFO`` or ``DEBUG``.

    Returns:
        The numeric logging level.

    Raises:
        ValueError: If the level name is unknown.
    """
    level = logging.getLevelNamesMapping().get(level_name.upper())
    if level is None:
        raise ValueError(f"Unknown log level: {level_name}")
    return level


def _build_processors() -> list[Any]:
    """Build the shared structlog processor pipeline.

    The pipeline enriches every event with a timestamp, log level, stack
    trace information, and exception details before rendering.

    Returns:
        A list of structlog processors shared by every environment.
    """
    return [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]


def configure_logging(settings: ApplicationSettings | None = None) -> None:
    """Configure structured logging for the application.

    In development the console renderer emits colorized, human-readable
    lines. In production the JSON renderer emits a single JSON object per
    line. The active level is controlled by ``settings.log_level``.

    Args:
        settings: Application settings. Defaults to the cached singleton.
    """
    settings = settings if settings is not None else get_settings()

    processors = _build_processors()
    if settings.app_env == Environment.PRODUCTION:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            _resolve_level(settings.log_level)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Return a named structured logger.

    The returned logger is lazily resolved against the current structlog
    configuration on its first use, so it can be created before
    :func:`configure_logging` is called. Every event carries the logger
    name in a ``logger`` field.

    Args:
        name: Logger name, typically the module ``__name__``.

    Returns:
        A bound structlog logger for the given name.
    """
    return cast(
        structlog.BoundLogger,
        structlog.get_logger(name).bind(logger=name),
    )
