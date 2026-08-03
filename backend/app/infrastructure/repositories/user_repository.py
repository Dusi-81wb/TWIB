"""SQLAlchemy User repository implementation.

This module implements
:class:`~app.domain.repositories.user_repository.UserRepository`
backed by SQLAlchemy 2.0 and
:class:`app.infrastructure.database.models.user_model.UserModel`.
It translates between the domain aggregate :class:`app.domain.users.user.User`
and the persistence layer without leaking database details to the domain.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.user_repository import UserRepository
from app.domain.users.role import UserRole
from app.domain.users.status import UserStatus
from app.domain.users.user import User
from app.domain.value_objects import (
    Email,
    Metadata,
    Name,
    Timestamp,
    UuidIdentity,
    Version,
)
from app.infrastructure.database.models.user_model import UserModel
from app.infrastructure.repositories.base_repository import BaseRepository


class SQLAlchemyUserRepository(
    BaseRepository[User, UserModel, UuidIdentity], UserRepository
):
    """SQLAlchemy implementation of the UserRepository contract.

    Handles persistence for User aggregates using AsyncSession and UserModel.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository bound to an AsyncSession.

        Args:
            session: The active AsyncSession.
        """
        super().__init__(session, UserModel)

    def _to_domain(self, model: UserModel) -> User:
        """Convert a UserModel ORM instance into a User domain aggregate root.

        Args:
            model: The UserModel instance.

        Returns:
            The reconstructed User domain aggregate root.
        """
        user = User(
            user_id=UuidIdentity(model.id),
            email=Email(model.email),
            display_name=Name(model.display_name),
            status=UserStatus(model.status),
            role=UserRole(model.role),
            created_at=Timestamp(model.created_at),
            updated_at=Timestamp(model.updated_at),
            metadata=Metadata(model.metadata_json),
            version=Version(model.version),
        )
        user.pull_domain_events()
        return user

    def _to_model(self, entity: User, existing: UserModel | None = None) -> UserModel:
        """Convert a User domain aggregate root into a UserModel ORM instance.

        Args:
            entity: The User aggregate root.
            existing: Optional existing UserModel to mutate.

        Returns:
            The populated UserModel.
        """
        if existing is not None:
            existing.email = entity.email.value
            existing.display_name = entity.display_name.value
            existing.status = entity.status.value
            existing.role = entity.role.value
            existing.metadata_json = dict(entity.metadata.value)
            existing.updated_at = entity.updated_at.value
            existing.version = entity.version.major
            return existing

        return UserModel(
            id=entity.user_id.value,
            email=entity.email.value,
            display_name=entity.display_name.value,
            status=entity.status.value,
            role=entity.role.value,
            created_at=entity.created_at.value,
            updated_at=entity.updated_at.value,
            metadata_json=dict(entity.metadata.value),
            version=entity.version.major,
        )

    async def find_by_id(self, id_: UuidIdentity) -> User | None:
        """Find a user by identity.

        Args:
            id_: The identity of the user to look up.

        Returns:
            The user aggregate, or None if not found.
        """
        return await self.get_by_id(id_)

    async def find_by_email(self, email: Email) -> User | None:
        """Find a user by email address.

        Args:
            email: The email address to look up.

        Returns:
            The user aggregate, or None if not found.
        """
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def exists_by_email(self, email: Email) -> bool:
        """Return whether a user with the email address exists.

        Args:
            email: The email address to check.

        Returns:
            True if a user with the email exists, False otherwise.
        """
        stmt = select(UserModel.id).where(UserModel.email == email.value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
