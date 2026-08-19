"""Authentication schemas package.

Exposes request and response schemas for registration, login, and logout endpoints:

- :class:`.RegisterRequest`: Registration request model.
- :class:`.RegisterResponse`: Registration response model.
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
from app.schemas.auth.register_request import RegisterRequest
from app.schemas.auth.register_response import RegisterResponse

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "LogoutResponse",
    "PermissionResponse",
    "RefreshRequest",
    "RefreshResponse",
    "RegisterRequest",
    "RegisterResponse",
    "UserInfoResponse",
]
