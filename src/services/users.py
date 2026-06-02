"""
User service layer.

This module provides the business logic layer for user operations,
including user creation with Gravatar avatar fetching.

:author: Artur
:version: 1.0.0
"""

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    """
    Service class for user business logic.

    Acts as an intermediary between API routes and the data access layer,
    delegating operations to :class:`UserRepository` and handling
    additional logic such as Gravatar avatar retrieval.

    :param db: SQLAlchemy async session
    :type db: AsyncSession
    """

    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate, role: str = "user"):
        """
        Create a new user with an optional Gravatar avatar.

        Attempts to fetch a Gravatar image based on the user's email;
        if Gravatar is unavailable, the avatar is set to None.

        :param body: User creation data
        :type body: UserCreate
        :param role: User role ("user" or "admin"), default "user"
        :type role: str
        :return: The newly created user
        :rtype: User
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar, role)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their primary key ID.

        :param user_id: ID of the user to retrieve
        :type user_id: int
        :return: The user if found, None otherwise
        :rtype: User | None
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.

        :param username: Username to look up
        :type username: str
        :return: The user if found, None otherwise
        :rtype: User | None
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by their email address.

        :param email: Email address to look up
        :type email: str
        :return: The user if found, None otherwise
        :rtype: User | None
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Mark a user's email as confirmed.

        :param email: Email address of the user to confirm
        :type email: str
        :return: None
        :rtype: None
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Update a user's avatar URL.

        :param email: Email address of the user
        :type email: str
        :param url: New avatar URL
        :type url: str
        :return: The updated user
        :rtype: User
        """
        return await self.repository.update_avatar_url(email, url)

    async def update_password(self, email: str, hashed_password: str):
        """
        Update a user's password hash.

        :param email: Email address of the user
        :type email: str
        :param hashed_password: The new bcrypt-hashed password
        :type hashed_password: str
        :return: The updated user
        :rtype: User
        """
        return await self.repository.update_password(email, hashed_password)
