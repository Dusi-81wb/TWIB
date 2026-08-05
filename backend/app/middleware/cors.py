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
    origins = settings.cors_origins
    if not origins:
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
