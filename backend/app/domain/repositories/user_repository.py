"""User repository interface.

The persistence contract for the :class:`~app.domain.users.user.User`
aggregate. Application services depend on this protocol, never on a concrete
database implementation, so persistence can be swapped without touching
business logic (Clean Architecture / Repository Pattern).

Only the interface is declared here. There is no SQLAlchemy, database, or
infrastructure code in the domain layer.
"""

from __future__ import annotations

from typing import Protocol

from app.domain.users.user import User
from app.domain.value_objects import Email, UuidIdentity


class UserRepository(Protocol):
    """Persistence contract for the :class:`User` aggregate.

    This repository exposes the business-oriented queries the application
    needs (looking up a user by email or identity, checking email uniqueness,
    and persisting or deleting a user) instead of an unrestricted generic CRUD
    surface.
    """

    async def find_by_email(self, email: Email) -> User | None:
        """Find a user by email address.

        Args:
            email: The email address to look up.

        Returns:
            The user, or ``None`` when no user has that email address.
        """
        ...

    async def find_by_id(self, id_: UuidIdentity) -> User | None:
        """Find a user by identity.

        Args:
            id_: The identity of the user to look up.

        Returns:
            The user, or ``None`` when no user has that identity.
        """
        ...

    async def exists_by_email(self, email: Email) -> bool:
        """Return whether a user with the email address exists.

        Args:
            email: The email address to check.

        Returns:
            True when a user already has that email address.
        """
        ...

    async def find_all(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        """Return a paginated list of users.

        Args:
            limit: Maximum number of users to return.
            offset: Number of users to skip.

        Returns:
            A list of User aggregates.
        """
        ...

    async def count(self) -> int:
        """Return the total number of users.

        Returns:
            The total count of users in the repository.
        """
        ...

    async def save(self, user: User) -> None:
        """Persist a user, inserting or updating it as needed.

        Args:
            user: The user aggregate to persist.
        """
        ...

    async def delete(self, id_: UuidIdentity) -> None:
        """Delete the user with the identity.

        Args:
            id_: The identity of the user to delete.
        """
        ...
