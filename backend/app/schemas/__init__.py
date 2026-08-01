"""Public schema package for the TWIB backend.

Reusable response, pagination, and common schemas are re-exported here so
modules can import them from ``app.schemas`` without deep imports.
"""

from app.schemas.common import (
    CreatedAt,
    EntityId,
    Metadata,
    Timestamp,
    TimestampedModel,
    UpdatedAt,
)
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.schemas.response import (
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    MessageResponse,
    SuccessResponse,
)

__all__ = [
    "CreatedAt",
    "EntityId",
    "Metadata",
    "Timestamp",
    "TimestampedModel",
    "UpdatedAt",
    "PaginatedResponse",
    "PaginationMeta",
    "ErrorDetail",
    "ErrorResponse",
    "HealthResponse",
    "MessageResponse",
    "SuccessResponse",
]
