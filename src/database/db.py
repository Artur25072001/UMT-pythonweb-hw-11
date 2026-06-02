"""
Database session management.

This module provides the database connection setup and session management
using SQLAlchemy's async engine and session maker.

:author: Artur
:version: 1.0.0
"""

import contextlib
from src.conf.config import settings

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseSessionManager:
    """
    Manages the database engine and session lifecycle.

    Provides an async context manager for database sessions with
    automatic rollback on errors.

    :ivar _engine: The SQLAlchemy async engine instance
    :ivar _session_maker: The async session factory
    """

    def __init__(self, url: str):
        """
        Initialize the database session manager.

        Creates the async engine and session maker for the given database URL.

        :param url: Database connection URL
        :type url: str
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Provide an async database session within a context manager.

        Yields a session that automatically rolls back on SQLAlchemy errors
        and closes when the context exits.

        :yield: An async SQLAlchemy session
        :rtype: AsyncGenerator[AsyncSession, None]
        :raises Exception: If the session maker is not initialized
        :raises SQLAlchemyError: If a database error occurs
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    FastAPI dependency that provides an async database session.

    :yield: An async SQLAlchemy session for request handling
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with sessionmanager.session() as session:
        yield session
