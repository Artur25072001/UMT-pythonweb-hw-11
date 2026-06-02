"""
Pydantic schemas for request/response data validation.

This module defines the data models used for API request validation
and response serialization, including contacts and user schemas.

:author: Artur
:version: 1.0.0
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import date


class ContactBase(BaseModel):
    """
    Base schema for contact data.

    :ivar first_name: Contact's first name (max 50 characters)
    :ivar last_name: Contact's last name (max 50 characters)
    :ivar email: Contact's email address (max 100 characters)
    :ivar phone: Contact's phone number (max 15 characters)
    :ivar birthday: Contact's date of birth
    """

    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=100)
    phone: str = Field(..., max_length=15)
    birthday: date


class ContactCreate(ContactBase):
    """
    Schema for creating a new contact.

    Inherits all fields from :class:`ContactBase`.
    """

    pass


class ContactUpdate(ContactBase):
    """
    Schema for updating an existing contact.

    All fields are optional for partial updates.
    """

    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    birthday: Optional[date] = None


class ContactResponse(ContactBase):
    """
    Schema for contact response data.

    Includes the contact ID and enables ORM mode.

    :ivar id: Unique identifier for the contact
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    """
    Schema for user response data.

    :ivar id: Unique identifier for the user
    :ivar username: User's username
    :ivar email: User's email address
    :ivar avatar: URL of the user's avatar image
    :ivar role: User role — "user" or "admin"
    """

    id: int
    username: str
    email: str
    avatar: str
    role: str = "user"

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    :ivar username: Desired username
    :ivar email: User's email address
    :ivar password: User's password (will be hashed)
    """

    username: str
    email: str
    password: str


class Token(BaseModel):
    """
    Schema for authentication token response.

    :ivar access_token: JWT access token string
    :ivar token_type: Token type (e.g., "bearer")
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Schema for requesting email confirmation.

    :ivar email: Email address to send confirmation to
    """

    email: EmailStr


class RequestPasswordReset(BaseModel):
    """
    Schema for requesting a password reset email.

    :ivar email: Email address to send the reset link to
    """

    email: EmailStr


class ResetPassword(BaseModel):
    """
    Schema for setting a new password after token verification.

    :ivar token: JWT password reset token
    :ivar new_password: The new password to set
    """

    token: str
    new_password: str
