"""
Authentication service and utilities.

This module provides authentication-related functionality including
password hashing, JWT token creation and validation, and user
authentication for FastAPI endpoints.

:author: Artur
:version: 1.0.0
"""

from datetime import datetime, timedelta, UTC
from typing import Optional

from src.conf.config import settings
from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.database.redis import get_redis

from src.services.users import UserService
from src.services.cache import get_cached_user, set_cached_user
from src.database.models import User


import bcrypt
import redis.asyncio as aioredis


class Hash:
    """
    Utility class for password hashing and verification using bcrypt.

    Provides methods to hash passwords and verify plain-text passwords
    against stored hashes.
    """

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain-text password against a bcrypt hash.

        :param plain_password: The plain-text password to verify
        :type plain_password: str
        :param hashed_password: The stored bcrypt hash
        :type hashed_password: str
        :return: True if the password matches, False otherwise
        :rtype: bool
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def get_password_hash(self, password: str) -> str:
        """
        Hash a password using bcrypt.

        :param password: The plain-text password to hash
        :type password: str
        :return: The bcrypt hash of the password
        :rtype: str
        :raises ValueError: If the password exceeds 72 bytes
        """
        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 bytes")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Create a JWT access token.

    :param data: Data to encode in the token (must include "sub" claim)
    :type data: dict
    :param expires_delta: Optional custom expiration time in seconds
    :type expires_delta: Optional[int]
    :return: Encoded JWT token string
    :rtype: str
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_email_token(data: dict):
    """
    Create a JWT token for email confirmation.

    Token is valid for 7 days.

    :param data: Data to encode in the token (must include "sub" claim with email)
    :type data: dict
    :return: Encoded JWT token string
    :rtype: str
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def create_password_reset_token(data: dict):
    """
    Create a short-lived JWT token for password reset.

    Token is valid for 15 minutes.

    :param data: Data to encode in the token (must include "sub" claim with email)
    :type data: dict
    :return: Encoded JWT token string
    :rtype: str
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def get_email_from_token(token: str):
    """
    Extract the email address from a JWT token.

    Used for both email confirmation and password reset tokens.

    :param token: JWT token
    :type token: str
    :return: The email address stored in the token
    :rtype: str
    :raises HTTPException 422: If the token is invalid
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Неправильний токен для перевірки електронної пошти",
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """
    FastAPI dependency to retrieve the currently authenticated user.

    Decodes the JWT token from the Authorization header and fetches
    the corresponding user from the Redis cache first, falling back
    to the database if the cache miss occurs.

    :param token: JWT access token from the Authorization header
    :type token: str
    :param db: Database session dependency
    :type db: Session
    :param redis: Redis client dependency
    :type redis: aioredis.Redis
    :return: The authenticated user
    :rtype: User
    :raises HTTPException 401: If the token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    # Try Redis cache first
    if redis:
        cached_user = await get_cached_user(redis, username)
        if cached_user is not None:
            return cached_user

    # Fallback to database
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception

    # Store in Redis cache for subsequent requests
    if redis:
        await set_cached_user(redis, user)

    return user


class RoleChecker:
    """
    FastAPI dependency factory that checks if the authenticated user
    has one of the allowed roles.

    Usage::

        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(get_current_user),
                                 _: bool = Depends(RoleChecker(["admin"]))):
            ...

    :param allowed_roles: List of role names that are permitted
    :type allowed_roles: list[str]
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, user: User = Depends(get_current_user)) -> bool:
        """
        Check the current user's role against the allowed list.

        :param user: The currently authenticated user
        :type user: User
        :return: True if the user has an allowed role
        :rtype: bool
        :raises HTTPException 403: If the user's role is not allowed
        """
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return True
