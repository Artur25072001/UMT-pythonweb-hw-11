"""
Unit tests for the UserRepository.

Tests cover all CRUD operations and special queries
by mocking the SQLAlchemy AsyncSession.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate


@pytest.fixture
def mock_session():
    """Create a mock async database session."""
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    """Create a UserRepository with the mocked session."""
    return UserRepository(mock_session)


@pytest.fixture
def sample_user():
    """Create a sample User instance for testing."""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pwd",
        avatar="http://avatar.url",
        confirmed=True,
        role="user",
    )


@pytest.fixture
def sample_user_create():
    """Create a sample UserCreate schema for testing."""
    return UserCreate(
        username="newuser",
        email="new@example.com",
        password="plain_password",
    )


# ===================== get_user_by_id =====================


@pytest.mark.asyncio
async def test_get_user_by_id_found(user_repository, mock_session, sample_user):
    """Should return a user when the ID exists."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_id(user_id=1)

    assert user is not None
    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_repository, mock_session):
    """Should return None when the ID does not exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_id(user_id=999)

    assert user is None


# ===================== get_user_by_username =====================


@pytest.mark.asyncio
async def test_get_user_by_username_found(user_repository, mock_session, sample_user):
    """Should return a user when the username exists."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_username(username="testuser")

    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_username_not_found(user_repository, mock_session):
    """Should return None when the username does not exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_username(username="nonexistent")

    assert user is None


# ===================== get_user_by_email =====================


@pytest.mark.asyncio
async def test_get_user_by_email_found(user_repository, mock_session, sample_user):
    """Should return a user when the email exists."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_email(email="test@example.com")

    assert user is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(user_repository, mock_session):
    """Should return None when the email does not exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_email(email="missing@example.com")

    assert user is None


# ===================== create_user =====================


@pytest.mark.asyncio
async def test_create_user_default_role(
    user_repository, mock_session, sample_user_create
):
    """Should create a new user with the default 'user' role."""
    result = await user_repository.create_user(body=sample_user_create)

    assert isinstance(result, User)
    assert result.username == "newuser"
    assert result.email == "new@example.com"
    assert result.hashed_password == "plain_password"
    assert result.role == "user"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_admin_role(user_repository, mock_session):
    """Should create a new user with the 'admin' role when specified."""
    body = UserCreate(
        username="adminuser",
        email="admin@example.com",
        password="admin_pass",
    )

    result = await user_repository.create_user(body=body, role="admin")

    assert isinstance(result, User)
    assert result.username == "adminuser"
    assert result.role == "admin"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_with_avatar(user_repository, mock_session):
    """Should create a new user with a provided avatar URL."""
    body = UserCreate(
        username="avataruser",
        email="avatar@example.com",
        password="pwd123",
    )

    result = await user_repository.create_user(
        body=body, avatar="http://avatar.url/photo.jpg"
    )

    assert result.username == "avataruser"
    assert result.avatar == "http://avatar.url/photo.jpg"
    assert result.role == "user"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


# ===================== confirmed_email =====================


@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session, sample_user):
    """Should mark a user's email as confirmed."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    await user_repository.confirmed_email(email="test@example.com")

    assert sample_user.confirmed is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_confirmed_email_user_not_found(user_repository, mock_session):
    """Should raise an error when the user email does not exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(AttributeError):
        await user_repository.confirmed_email(email="missing@example.com")


# ===================== update_avatar_url =====================


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session, sample_user):
    """Should update the user's avatar URL and return the updated user."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    new_avatar_url = "http://new-avatar.url/new.jpg"
    result = await user_repository.update_avatar_url(
        email="test@example.com", url=new_avatar_url
    )

    assert result.avatar == new_avatar_url
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_user)


# ===================== update_password =====================


@pytest.mark.asyncio
async def test_update_password(user_repository, mock_session, sample_user):
    """Should update the user's hashed password."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    new_hashed_password = "new_hashed_password_value"
    result = await user_repository.update_password(
        email="test@example.com", hashed_password=new_hashed_password
    )

    assert result.hashed_password == new_hashed_password
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(sample_user)
