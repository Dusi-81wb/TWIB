"""Authentication schemas package.

Exposes request and response schemas for login and logout endpoints:

- :class:`.LoginRequest`: Credentials request model.
- :class:`.LoginResponse`: Token and user details response.
- :class:`.UserInfoResponse`: User summary model.
- :class:`.LogoutResponse`: Logout status model.
"""

from app.schemas.auth.login_request import LoginRequest
from app.schemas.auth.login_response import (
    LoginResponse,
    LogoutResponse,
    UserInfoResponse,
)
from app.schemas.auth.permission_response import PermissionResponse
from app.schemas.auth.refresh_request import RefreshRequest
from app.schemas.auth.refresh_response import RefreshResponse

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "LogoutResponse",
    "PermissionResponse",
    "RefreshRequest",
    "RefreshResponse",
    "UserInfoResponse",
]
