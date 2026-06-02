"""
Redis connection manager.

This module provides a Redis client singleton and a FastAPI dependency
for accessing Redis throughout the application. The client is used for
caching user data to reduce database load.

:author: Artur
:version: 1.0.0
"""

from typing import Optional

import redis.asyncio as aioredis

from src.conf.config import settings


class RedisClient:
    """
    Manages the Redis async connection.

    Provides a lazily-initialised Redis client that can be started
    and closed as part of the application lifespan.

    :ivar client: The async Redis client instance
    :type client: Optional[aioredis.Redis]
    """

    def __init__(self) -> None:
        self.client: Optional[aioredis.Redis] = None

    async def init(self) -> None:
        """
        Initialise the Redis client using the configured URL.

        :return: None
        :rtype: None
        """
        self.client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def close(self) -> None:
        """
        Close the Redis connection gracefully.

        :return: None
        :rtype: None
        """
        if self.client:
            await self.client.close()
            self.client = None


redis_client = RedisClient()


async def get_redis() -> aioredis.Redis:
    """
    FastAPI dependency that provides the Redis client instance.

    :return: The async Redis client
    :rtype: aioredis.Redis
    """
    return redis_client.client
