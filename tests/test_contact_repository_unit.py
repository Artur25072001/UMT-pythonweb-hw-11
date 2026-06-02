from datetime import date

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contact import ContactRepository
from src.schemas import ContactBase, ContactUpdate, ContactCreate


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, first_name="John", last_name="Doe", user=user)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contacts = await contact_repository.get_contacts(skip=0, limit=10, user=user)

    # Assertions
    assert len(contacts) == 1
    assert contacts[0].first_name == "John"
    assert contacts[0].last_name == "Doe"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1, first_name="John", last_name="Doe", user=user
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    contact = await contact_repository.get_contact_by_id(contact_id=1, user=user)

    # Assertions
    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactCreate(
        first_name="new contact",
        last_name="new contact",
        email="new@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
    )

    # Mock refresh to set an id on the created contact
    async def refresh_side_effect(instance):
        instance.id = 1

    mock_session.refresh = AsyncMock(side_effect=refresh_side_effect)

    # Mock the internal get_contact_by_id call
    mock_get_result = MagicMock()
    expected_contact = Contact(
        id=1,
        first_name="new contact",
        last_name="new contact",
        email="new@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
        user=user,
    )
    mock_get_result.scalar_one_or_none.return_value = expected_contact
    mock_session.execute = AsyncMock(return_value=mock_get_result)

    # Call method
    result = await contact_repository.create_contact(body=contact_data, user=user)

    # Assertions
    assert isinstance(result, Contact)
    assert result.first_name == "new contact"
    assert result.last_name == "new contact"
    assert result.email == "new@example.com"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    # Setup
    contact_data = ContactUpdate(
        first_name="updated first name", last_name="updated last name"
    )
    existing_contact = Contact(
        id=1, first_name="old first name", last_name="old last name", user=user
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.update_contact(
        contact_id=1, body=contact_data, user=user
    )

    # Assertions
    assert result is not None
    assert result.first_name == "updated first name"
    assert result.last_name == "updated last name"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    # Setup
    existing_contact = Contact(
        id=1, first_name="contact to delete", last_name="contact to delete", user=user
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.remove_contact(contact_id=1, user=user)

    # Assertions
    assert result is not None
    assert result.first_name == "contact to delete"
    assert result.last_name == "contact to delete"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()
