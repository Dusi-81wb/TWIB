"""TWIB backend application entry point.

This module only starts the application. The FastAPI instance is created
through the application factory and must never be defined at module level.
"""

from app.application import create_application

app = create_application()
