"""
Unit tests for the database session manager.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.database.db import DatabaseSessionManager


@pytest.fixture
def mock_engine():
    """Create a mock async engine."""
    with patch("src.database.db.create_async_engine") as mock_create:
        mock_engine = MagicMock()
        mock_create.return_value = mock_engine
        yield mock_engine


def test_db_session_manager_init(mock_engine):
    """Should initialise the engine and session maker."""
    manager = DatabaseSessionManager("sqlite+aiosqlite:///test.db")
    assert manager._engine is not None
    assert manager._session_maker is not None


@pytest.mark.asyncio
async def test_db_session_success(mock_engine):
    """Should yield a session and close it on exit."""
    manager = DatabaseSessionManager("sqlite+aiosqlite:///test.db")
    mock_session = AsyncMock()
    manager._session_maker = MagicMock(return_value=mock_session)

    async with manager.session() as session:
        assert session is mock_session

    mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_db_session_rollback_on_error(mock_engine):
    """Should rollback the session on SQLAlchemyError."""
    manager = DatabaseSessionManager("sqlite+aiosqlite:///test.db")
    mock_session = AsyncMock()
    manager._session_maker = MagicMock(return_value=mock_session)

    with pytest.raises(SQLAlchemyError):
        async with manager.session() as session:
            raise SQLAlchemyError("test error")

    mock_session.rollback.assert_awaited_once()
    mock_session.close.assert_awaited_once()


def test_db_session_not_initialized(mock_engine):
    """Should raise Exception if session maker is None."""
    manager = DatabaseSessionManager("sqlite+aiosqlite:///test.db")
    manager._session_maker = None

    with pytest.raises(Exception, match="Database session is not initialized"):
        # Need to iterate the async generator
        async def run():
            async with manager.session() as session:
                pass

        import asyncio

        asyncio.run(run())
