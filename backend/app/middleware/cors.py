"""CORS middleware.

Configures FastAPI's ``CORSMiddleware`` from the application settings.
Allowed origins are read from ``settings.cors_origins`` and are never
hardcoded.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import ApplicationSettings


def configure_cors(application: FastAPI, settings: ApplicationSettings) -> None:
    """Add CORS middleware to the application from settings.

    Args:
        application: The FastAPI application to configure.
        settings: Application settings providing the allowed origins.
    """
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
