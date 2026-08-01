"""API version 1 package."""

from fastapi import APIRouter

from app.api.v1.health import health_router
from app.core.constants import API_V1_PREFIX

api_v1_router = APIRouter(prefix=API_V1_PREFIX)
api_v1_router.include_router(health_router)

__all__ = ["api_v1_router"]
