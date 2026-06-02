"""
Contact repository for database operations.

This module provides the data access layer for Contact entities,
handling CRUD operations and specialized queries like birthday lookups.

:author: Artur
:version: 1.0.0
"""

import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactUpdate, ContactCreate


class ContactRepository:
    """
    Repository class for Contact database operations.

    Provides methods for creating, reading, updating, and deleting contacts,
    as well as querying contacts by various criteria.

    :param session: SQLAlchemy async session
    :type session: AsyncSession
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        user: User,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> List[Contact]:
        """
        Retrieve a list of contacts for a user with optional filtering.

        :param skip: Number of records to skip (pagination offset)
        :type skip: int
        :param limit: Maximum number of records to return
        :type limit: int
        :param user: The authenticated user
        :type user: User
        :param first_name: Optional filter by first name (case-insensitive partial match)
        :type first_name: Optional[str]
        :param last_name: Optional filter by last name (case-insensitive partial match)
        :type last_name: Optional[str]
        :param email: Optional filter by email (case-insensitive partial match)
        :type email: Optional[str]
        :return: List of matching contacts
        :rtype: List[Contact]
        """
        stmt = select(Contact).filter_by(user=user)
        if first_name:
            stmt = stmt.filter(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.filter(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            stmt = stmt.filter(Contact.email.ilike(f"%{email}%"))

        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieve a single contact by its ID for a specific user.

        :param contact_id: ID of the contact to retrieve
        :type contact_id: int
        :param user: The authenticated user
        :type user: User
        :return: The contact if found, None otherwise
        :rtype: Contact | None
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate, user: User) -> Contact:
        """
        Create a new contact for a user.

        :param body: Contact creation data
        :type body: ContactCreate
        :param user: The authenticated user
        :type user: User
        :return: The newly created contact
        :rtype: Contact
        """
        contact = Contact(**body.model_dump(), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Delete a contact by its ID for a specific user.

        :param contact_id: ID of the contact to delete
        :type contact_id: int
        :param user: The authenticated user
        :type user: User
        :return: The deleted contact if found, None otherwise
        :rtype: Contact | None
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User
    ) -> Contact | None:
        """
        Update an existing contact by its ID for a specific user.

        Only the fields provided in the body will be updated (partial update).

        :param contact_id: ID of the contact to update
        :type contact_id: int
        :param body: Contact update data (partial)
        :type body: ContactUpdate
        :param user: The authenticated user
        :type user: User
        :return: The updated contact if found, None otherwise
        :rtype: Contact | None
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            update_data = body.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def get_upcoming_birthdays(self, user: User) -> List[Contact]:
        """
        Retrieve contacts with birthdays occurring within the next 7 days.

        :param user: The authenticated user
        :type user: User
        :return: List of contacts with upcoming birthdays
        :rtype: List[Contact]
        """
        today = datetime.date.today()
        upcoming_date = today + datetime.timedelta(days=7)
        stmt = select(Contact).filter_by(user=user)
        result = await self.db.execute(stmt)
        all_contacts = result.scalars().all()
        near_birthdays = []
        for contact in all_contacts:
            if contact.birthday:
                try:
                    bday_this_year = contact.birthday.replace(year=today.year)
                except ValueError:
                    bday_this_year = contact.birthday.replace(
                        year=today.year, month=3, day=1
                    )
                if today <= bday_this_year <= upcoming_date:
                    near_birthdays.append(contact)

        return near_birthdays
