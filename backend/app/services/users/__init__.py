"""User services package.

Provides the application service for user management:

- :class:`.UserService`: CRUD operations on users.
"""

from app.services.users.user_service import UserService

__all__ = ["UserService"]
