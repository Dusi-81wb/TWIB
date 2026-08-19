"""User schemas package.

Exposes request and response schemas for user management endpoints:

- :class:`.UserResponse`: Individual user detail response.
- :class:`.UserListResponse`: Paginated user list response.
- :class:`.UpdateProfileRequest`: Self-service profile update request.
- :class:`.UpdateUserRequest`: Admin user update request.
"""

from app.schemas.users.update_user_request import (
    UpdateProfileRequest,
    UpdateUserRequest,
)
from app.schemas.users.user_response import UserListResponse, UserResponse

__all__ = [
    "UpdateProfileRequest",
    "UpdateUserRequest",
    "UserListResponse",
    "UserResponse",
]
