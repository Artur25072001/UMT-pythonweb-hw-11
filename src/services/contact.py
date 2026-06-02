"""
Contact service layer.

This module provides the business logic layer for contact operations,
delegating database operations to the ContactRepository.

:author: Artur
:version: 1.0.0
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contact import ContactRepository
from src.schemas import ContactUpdate, ContactCreate
from src.database.models import User


class ContactService:
    """
    Service class for contact business logic.

    Acts as an intermediary between API routes and the data access layer,
    delegating CRUD operations to :class:`ContactRepository`.

    :param db: SQLAlchemy async session
    :type db: AsyncSession
    """

    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreate, user: User):
        """
        Create a new contact for a user.

        :param body: Contact creation data
        :type body: ContactCreate
        :param user: The authenticated user
        :type user: User
        :return: The newly created contact
        :rtype: Contact
        """
        return await self.repository.create_contact(body, user)

    async def get_upcoming_birthdays(self, user: User):
        """
        Retrieve contacts with upcoming birthdays within the next 7 days.

        :param user: The authenticated user
        :type user: User
        :return: List of contacts with upcoming birthdays
        :rtype: List[Contact]
        """
        return await self.repository.get_upcoming_birthdays(user)

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: str,
        last_name: str,
        email: str,
        user: User,
    ):
        """
        Retrieve a list of contacts for a user with optional filtering.

        :param skip: Number of records to skip (pagination offset)
        :type skip: int
        :param limit: Maximum number of records to return
        :type limit: int
        :param first_name: Optional filter by first name
        :type first_name: str
        :param last_name: Optional filter by last name
        :type last_name: str
        :param email: Optional filter by email
        :type email: str
        :param user: The authenticated user
        :type user: User
        :return: List of matching contacts
        :rtype: List[Contact]
        """
        return await self.repository.get_contacts(
            skip=skip,
            limit=limit,
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieve a single contact by its ID for a user.

        :param contact_id: ID of the contact to retrieve
        :type contact_id: int
        :param user: The authenticated user
        :type user: User
        :return: The contact if found, None otherwise
        :rtype: Contact | None
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        """
        Update an existing contact by its ID for a user.

        :param contact_id: ID of the contact to update
        :type contact_id: int
        :param body: Contact update data (partial update supported)
        :type body: ContactUpdate
        :param user: The authenticated user
        :type user: User
        :return: The updated contact if found, None otherwise
        :rtype: Contact | None
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Delete a contact by its ID for a user.

        :param contact_id: ID of the contact to delete
        :type contact_id: int
        :param user: The authenticated user
        :type user: User
        :return: The deleted contact if found, None otherwise
        :rtype: Contact | None
        """
        return await self.repository.remove_contact(contact_id, user)
