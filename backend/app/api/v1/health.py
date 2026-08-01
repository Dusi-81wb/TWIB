"""Health check endpoints for API version 1."""

from fastapi import APIRouter

from app.core.constants import SERVICE_NAME, VERSION

health_router = APIRouter()


@health_router.get("/health")
def get_health() -> dict[str, str]:
    """Return the current health status of the service.

    Returns:
        A dictionary describing the service health, name, and version.
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": VERSION,
    }
