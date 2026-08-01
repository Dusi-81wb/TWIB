"""Root API router.

Aggregates every versioned API router under the ``/api`` prefix.
"""

from fastapi import APIRouter

from app.api.v1 import api_v1_router
from app.core.constants import API_PREFIX

api_router = APIRouter(prefix=API_PREFIX)
api_router.include_router(api_v1_router)
