"""
User repository for database operations.

This module provides the data access layer for User entities,
handling CRUD operations and user lookup queries.

:author: Artur
:version: 1.0.0
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """
    Repository class for User database operations.

    Provides methods for creating users and looking up users by
    various criteria such as ID, username, or email.

    :param session: SQLAlchemy async session
    :type session: AsyncSession
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their primary key ID.

        :param user_id: ID of the user to retrieve
        :type user_id: int
        :return: The user if found, None otherwise
        :rtype: User | None
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        :param username: Username to look up
        :type username: str
        :return: The user if found, None otherwise
        :rtype: User | None
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.

        :param email: Email address to look up
        :type email: str
        :return: The user if found, None otherwise
        :rtype: User | None
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(
        self, body: UserCreate, avatar: str = None, role: str = "user"
    ) -> User:
        """
        Create a new user in the database.

        :param body: User creation data
        :type body: UserCreate
        :param avatar: Optional URL for the user's avatar
        :type avatar: str
        :param role: User role — "user" or "admin" (default: "user")
        :type role: str
        :return: The newly created user
        :rtype: User
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar,
            role=role,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Mark a user's email as confirmed.

        :param email: Email address of the user to confirm
        :type email: str
        :return: None
        :rtype: None
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update a user's avatar URL.

        :param email: Email address of the user
        :type email: str
        :param url: New avatar URL
        :type url: str
        :return: The updated user
        :rtype: User
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_password(self, email: str, hashed_password: str) -> User:
        """
        Update a user's password hash.

        :param email: Email address of the user
        :type email: str
        :param hashed_password: The new bcrypt-hashed password
        :type hashed_password: str
        :return: The updated user
        :rtype: User
        """
        user = await self.get_user_by_email(email)
        user.hashed_password = hashed_password
        await self.db.commit()
        await self.db.refresh(user)
        return user
