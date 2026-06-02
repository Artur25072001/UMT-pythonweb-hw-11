"""
Unit tests for the Redis connection manager.
"""

from unittest.mock import AsyncMock, patch

import pytest
import redis.asyncio as aioredis

from src.database.redis import RedisClient, redis_client, get_redis


@pytest.mark.asyncio
async def test_redis_client_init():
    """Should initialise the Redis client with the configured URL."""
    client = RedisClient()
    assert client.client is None

    with patch("src.database.redis.aioredis.from_url") as mock_from_url:
        mock_redis = AsyncMock()
        mock_from_url.return_value = mock_redis

        await client.init()

        mock_from_url.assert_called_once()
        assert client.client is mock_redis


@pytest.mark.asyncio
async def test_redis_client_close():
    """Should close the Redis connection gracefully."""
    client = RedisClient()
    mock_redis = AsyncMock()
    client.client = mock_redis

    await client.close()

    mock_redis.close.assert_awaited_once()
    assert client.client is None


@pytest.mark.asyncio
async def test_redis_client_close_no_client():
    """Should handle close when no client is initialised."""
    client = RedisClient()
    client.client = None

    # Should not raise any error
    await client.close()
    assert client.client is None


@pytest.mark.asyncio
async def test_get_redis_no_client():
    """Should return None when Redis is not initialised."""
    redis_client.client = None
    result = await get_redis()
    assert result is None


@pytest.mark.asyncio
async def test_get_redis_with_client():
    """Should return the Redis client when initialised."""
    mock_redis = AsyncMock()
    redis_client.client = mock_redis
    result = await get_redis()
    assert result is mock_redis
