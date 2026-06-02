"""
User caching service for Redis.

Provides helper functions to store, retrieve, and delete user data
in Redis, reducing the number of database queries for authenticated
requests.

:author: Artur
:version: 1.0.0
"""

import json
from datetime import datetime

import redis.asyncio as aioredis

from src.database.models import User
from src.conf.config import settings

CACHE_TTL = settings.JWT_EXPIRATION_SECONDS
USER_CACHE_PREFIX = "user:"


def _user_to_dict(user: User) -> dict:
    """
    Serialise a User ORM instance to a JSON-serialisable dictionary.

    :param user: The user ORM instance
    :type user: User
    :return: Dictionary representation of the user
    :rtype: dict
    """
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "hashed_password": user.hashed_password,
        "avatar": user.avatar,
        "confirmed": user.confirmed,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def _dict_to_user(data: dict) -> User:
    """
    Reconstruct a User ORM instance from a dictionary.

    :param data: Dictionary containing user fields
    :type data: dict
    :return: A User ORM instance (not bound to any session)
    :rtype: User
    """
    if data.get("created_at"):
        data["created_at"] = datetime.fromisoformat(data["created_at"])
    return User(**data)


async def get_cached_user(redis: aioredis.Redis, username: str) -> User | None:
    """
    Retrieve a cached user by username.

    :param redis: Redis client instance
    :type redis: aioredis.Redis
    :param username: The username to look up
    :type username: str
    :return: The cached user if found, None otherwise
    :rtype: User | None
    """
    key = f"{USER_CACHE_PREFIX}{username}"
    data = await redis.get(key)
    if data is None:
        return None
    try:
        return _dict_to_user(json.loads(data))
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


async def set_cached_user(redis: aioredis.Redis, user: User) -> None:
    """
    Store a user in the Redis cache.

    :param redis: Redis client instance
    :type redis: aioredis.Redis
    :param user: The user to cache
    :type user: User
    :return: None
    :rtype: None
    """
    key = f"{USER_CACHE_PREFIX}{user.username}"
    data = json.dumps(_user_to_dict(user))
    await redis.setex(key, CACHE_TTL, data)


async def delete_cached_user(redis: aioredis.Redis, username: str) -> None:
    """
    Remove a user from the Redis cache.

    :param redis: Redis client instance
    :type redis: aioredis.Redis
    :param username: The username whose cache entry to delete
    :type username: str
    :return: None
    :rtype: None
    """
    key = f"{USER_CACHE_PREFIX}{username}"
    await redis.delete(key)
