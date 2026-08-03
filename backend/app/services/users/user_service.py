"""User application service.

Orchestrates user management operations using the Unit of Work,
repositories, and domain aggregate methods. No direct database access;
all persistence goes through the repository layer.
"""

from __future__ import annotations

import uuid

from app.domain.exceptions import BusinessRuleViolation, EntityNotFound
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.users.role import UserRole
from app.domain.users.status import UserStatus
from app.domain.users.user import User
from app.domain.value_objects import Email, Name, UuidIdentity


class UserService:
    """Application service managing user lifecycle operations.

    All methods interact with the persistence layer exclusively through
    the Unit of Work and its repositories.

    Attributes:
        _uow: Unit of Work for repository access.
    """

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        """Initialize the user service.

        Args:
            unit_of_work: Unit of Work for repository access.
        """
        self._uow = unit_of_work

    async def get_current_user(self, user_id: str) -> User:
        """Retrieve the currently authenticated user by ID.

        Args:
            user_id: UUID string of the authenticated user.

        Returns:
            The User domain aggregate.

        Raises:
            EntityNotFound: If user does not exist.
        """
        user = await self._find_user_or_raise(user_id)
        return user

    async def get_user(self, user_id: str) -> User:
        """Retrieve a user by ID.

        Args:
            user_id: UUID string of the target user.

        Returns:
            The User domain aggregate.

        Raises:
            EntityNotFound: If user does not exist.
        """
        return await self._find_user_or_raise(user_id)

    async def list_users(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        """List users with pagination.

        Args:
            limit: Maximum number of users to return.
            offset: Number of users to skip.

        Returns:
            Tuple of (list of User aggregates, total count).
        """
        async with self._uow as uow:
            users = await uow.users.find_all(limit=limit, offset=offset)
            total = await uow.users.count()
        return users, total

    async def update_profile(
        self,
        user_id: str,
        display_name: str | None = None,
        email: str | None = None,
    ) -> User:
        """Update the authenticated user's own profile.

        Args:
            user_id: UUID string of the authenticated user.
            display_name: Optional new display name.
            email: Optional new email address.

        Returns:
            The updated User domain aggregate.

        Raises:
            EntityNotFound: If user does not exist.
            BusinessRuleViolation: If a domain rule is violated.
        """
        async with self._uow as uow:
            user = await self._find_user_in_uow(uow, user_id)
            self._apply_profile_changes(user, display_name, email)
            await uow.users.save(user)
            await uow.commit()
        return user

    async def update_user(
        self,
        user_id: str,
        display_name: str | None = None,
        email: str | None = None,
        role: str | None = None,
        status: str | None = None,
    ) -> User:
        """Admin-level update of a user's profile, role, or status.

        Args:
            user_id: UUID string of the target user.
            display_name: Optional new display name.
            email: Optional new email address.
            role: Optional new role string.
            status: Optional new status string.

        Returns:
            The updated User domain aggregate.

        Raises:
            EntityNotFound: If user does not exist.
            BusinessRuleViolation: If a domain rule is violated.
        """
        async with self._uow as uow:
            user = await self._find_user_in_uow(uow, user_id)

            self._apply_profile_changes(user, display_name, email)

            if role is not None:
                self._apply_role_change(user, role)

            if status is not None:
                self._apply_status_change(user, status)

            await uow.users.save(user)
            await uow.commit()
        return user

    async def deactivate_user(self, user_id: str) -> User:
        """Deactivate a user (set status to DISABLED).

        Args:
            user_id: UUID string of the target user.

        Returns:
            The deactivated User domain aggregate.

        Raises:
            EntityNotFound: If user does not exist.
            BusinessRuleViolation: If a domain rule is violated.
        """
        async with self._uow as uow:
            user = await self._find_user_in_uow(uow, user_id)
            user.deactivate()
            await uow.users.save(user)
            await uow.commit()
        return user

    async def activate_user(self, user_id: str) -> User:
        """Activate a user (set status to ACTIVE).

        Args:
            user_id: UUID string of the target user.

        Returns:
            The activated User domain aggregate.

        Raises:
            EntityNotFound: If user does not exist.
            BusinessRuleViolation: If a domain rule is violated.
        """
        async with self._uow as uow:
            user = await self._find_user_in_uow(uow, user_id)
            user.activate()
            await uow.users.save(user)
            await uow.commit()
        return user

    async def delete_user(self, user_id: str) -> User:
        """Soft-delete a user (set status to DELETED).

        Args:
            user_id: UUID string of the target user.

        Returns:
            The deleted User domain aggregate.

        Raises:
            EntityNotFound: If user does not exist.
            BusinessRuleViolation: If a domain rule is violated.
        """
        async with self._uow as uow:
            user = await self._find_user_in_uow(uow, user_id)
            user.delete()
            await uow.users.save(user)
            await uow.commit()
        return user

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _find_user_or_raise(self, user_id: str) -> User:
        """Find a user by ID or raise EntityNotFound.

        Args:
            user_id: UUID string of the target user.

        Returns:
            The User domain aggregate.

        Raises:
            EntityNotFound: If user does not exist.
        """
        try:
            uid = uuid.UUID(user_id)
        except ValueError as err:
            raise EntityNotFound(
                f"User '{user_id}' not found",
            ) from err

        async with self._uow as uow:
            user = await uow.users.find_by_id(UuidIdentity(uid))

        if user is None:
            raise EntityNotFound(f"User '{user_id}' not found")
        return user

    async def _find_user_in_uow(
        self,
        uow: UnitOfWork,
        user_id: str,
    ) -> User:
        """Find a user within an active UoW or raise EntityNotFound.

        Args:
            uow: The active Unit of Work.
            user_id: UUID string of the target user.

        Returns:
            The User domain aggregate.

        Raises:
            EntityNotFound: If user does not exist.
        """
        try:
            uid = uuid.UUID(user_id)
        except ValueError as err:
            raise EntityNotFound(
                f"User '{user_id}' not found",
            ) from err

        user = await uow.users.find_by_id(UuidIdentity(uid))
        if user is None:
            raise EntityNotFound(f"User '{user_id}' not found")
        return user

    @staticmethod
    def _apply_profile_changes(
        user: User,
        display_name: str | None,
        email: str | None,
    ) -> None:
        """Apply display name and email changes to a user aggregate.

        Args:
            user: The User aggregate to modify.
            display_name: Optional new display name.
            email: Optional new email address.
        """
        if display_name is not None:
            user.change_display_name(Name(display_name))
        if email is not None:
            user.change_email(Email(email))

    @staticmethod
    def _apply_role_change(user: User, role: str) -> None:
        """Apply a role change to a user aggregate.

        Directly sets the internal ``_role`` attribute after validating
        the role string against the :class:`UserRole` enum.

        Args:
            user: The User aggregate to modify.
            role: The new role string.

        Raises:
            BusinessRuleViolation: If the role string is invalid.
        """
        try:
            new_role = UserRole(role)
        except ValueError as err:
            raise BusinessRuleViolation(f"Invalid role: '{role}'") from err
        user._role = new_role
        user._touch()

    @staticmethod
    def _apply_status_change(user: User, status: str) -> None:
        """Apply a status transition via domain methods.

        Maps the requested status string to the appropriate domain method
        (activate, deactivate, suspend, restore, delete).

        Args:
            user: The User aggregate to modify.
            status: The target status string.

        Raises:
            BusinessRuleViolation: If the status string is invalid or
                the transition is not allowed.
        """
        try:
            target = UserStatus(status)
        except ValueError as err:
            raise BusinessRuleViolation(f"Invalid status: '{status}'") from err

        transitions = {
            UserStatus.ACTIVE: user.activate,
            UserStatus.DISABLED: user.deactivate,
            UserStatus.SUSPENDED: user.suspend,
            UserStatus.DELETED: user.delete,
        }

        handler = transitions.get(target)
        if handler is None:
            raise BusinessRuleViolation(f"Cannot transition to status '{status}'")
        handler()
