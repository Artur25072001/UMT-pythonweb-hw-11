"""
Unit tests for the Redis cache service.

Tests serialisation helpers and public cache functions
using a mocked async Redis client.
"""

import json
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import redis.asyncio as aioredis

from src.database.models import User
from src.services.cache import (
    _user_to_dict,
    _dict_to_user,
    get_cached_user,
    set_cached_user,
    delete_cached_user,
    USER_CACHE_PREFIX,
    CACHE_TTL,
)


@pytest.fixture
def mock_redis():
    """Create a mock async Redis client without spec to allow await on all methods."""
    mock = MagicMock()
    mock.get = AsyncMock()
    mock.setex = AsyncMock()
    mock.delete = AsyncMock()
    return mock


@pytest.fixture
def sample_user():
    """Create a sample User instance with all fields."""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pwd",
        avatar="http://avatar.url",
        confirmed=True,
        role="user",
        created_at=datetime(2026, 1, 15, 10, 30, 0),
    )


@pytest.fixture
def sample_user_no_avatar():
    """Create a user with null avatar and no created_at."""
    return User(
        id=2,
        username="noavatar",
        email="noavatar@example.com",
        hashed_password="hash",
        avatar=None,
        confirmed=False,
        role="user",
        created_at=None,
    )


# ===================== _user_to_dict =====================


def test_user_to_dict(sample_user):
    """Should serialise a User to a dictionary."""
    result = _user_to_dict(sample_user)
    assert result["id"] == 1
    assert result["username"] == "testuser"
    assert result["email"] == "test@example.com"
    assert result["hashed_password"] == "hashed_pwd"
    assert result["avatar"] == "http://avatar.url"
    assert result["confirmed"] is True
    assert result["role"] == "user"
    assert result["created_at"] == "2026-01-15T10:30:00"


def test_user_to_dict_nullable_fields(sample_user_no_avatar):
    """Should handle null avatar and created_at."""
    result = _user_to_dict(sample_user_no_avatar)
    assert result["avatar"] is None
    assert result["created_at"] is None
    assert result["confirmed"] is False


# ===================== _dict_to_user =====================


def test_dict_to_user(sample_user):
    """Should reconstruct a User from a dictionary."""
    data = _user_to_dict(sample_user)
    user = _dict_to_user(data)
    assert isinstance(user, User)
    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_pwd"
    assert user.avatar == "http://avatar.url"
    assert user.confirmed is True
    assert user.role == "user"
    assert user.created_at == datetime(2026, 1, 15, 10, 30, 0)


def test_dict_to_user_nullable(sample_user_no_avatar):
    """Should handle null avatar and created_at fields."""
    data = _user_to_dict(sample_user_no_avatar)
    user = _dict_to_user(data)
    assert user.avatar is None
    assert user.created_at is None
    assert user.confirmed is False


# ===================== get_cached_user =====================


@pytest.mark.asyncio
async def test_get_cached_user_found(mock_redis, sample_user):
    """Should return a cached user when the key exists."""
    cached_data = json.dumps(_user_to_dict(sample_user))
    mock_redis.get.return_value = cached_data

    user = await get_cached_user(mock_redis, "testuser")

    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    mock_redis.get.assert_awaited_once_with(f"{USER_CACHE_PREFIX}testuser")


@pytest.mark.asyncio
async def test_get_cached_user_not_found(mock_redis):
    """Should return None when the key does not exist."""
    mock_redis.get.return_value = None

    user = await get_cached_user(mock_redis, "unknown")

    assert user is None


@pytest.mark.asyncio
async def test_get_cached_user_invalid_json(mock_redis):
    """Should return None when the cached data is malformed."""
    mock_redis.get.return_value = "not valid json"

    user = await get_cached_user(mock_redis, "testuser")

    assert user is None


# ===================== set_cached_user =====================


@pytest.mark.asyncio
async def test_set_cached_user(mock_redis, sample_user):
    """Should store a user in Redis with TTL."""
    await set_cached_user(mock_redis, sample_user)

    expected_key = f"{USER_CACHE_PREFIX}testuser"
    expected_data = json.dumps(_user_to_dict(sample_user))
    mock_redis.setex.assert_awaited_once_with(expected_key, CACHE_TTL, expected_data)


# ===================== delete_cached_user =====================


@pytest.mark.asyncio
async def test_delete_cached_user(mock_redis):
    """Should remove a user from Redis."""
    await delete_cached_user(mock_redis, "testuser")

    mock_redis.delete.assert_awaited_once_with(f"{USER_CACHE_PREFIX}testuser")
