from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import date


class ContactBase(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=100)
    phone: str = Field(..., max_length=15)
    birthday: date


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    birthday: Optional[date] = None


class ContactResponse(ContactBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
