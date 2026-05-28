from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contact import ContactRepository
from src.schemas import ContactUpdate, ContactCreate
from src.database.models import User


class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreate, user: User):
        return await self.repository.create_contact(body, user)

    async def get_upcoming_birthdays(self):
        return await self.repository.get_upcoming_birthdays()

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: str,
        last_name: str,
        email: str,
        user: User,
    ):
        return await self.repository.get_contacts(
            skip, limit, first_name, last_name, email, user
        )

    async def get_contact(self, contact_id: int, user: User):
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        return await self.repository.remove_contact(contact_id, user)
