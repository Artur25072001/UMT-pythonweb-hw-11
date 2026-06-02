"""
SQLAlchemy ORM models.

This module defines the database models for the application,
including User and Contact entities.

:author: Artur
:version: 1.0.0
"""

from sqlalchemy import String, func
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase


from datetime import date
from sqlalchemy import Date
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Provides the declarative base for database model definitions.
    """

    pass


class User(Base):
    """
    User model representing an application user.

    :ivar id: Primary key identifier
    :ivar username: Unique username for the user
    :ivar email: Unique email address
    :ivar hashed_password: Bcrypt-hashed password
    :ivar created_at: Timestamp of account creation
    :ivar avatar: URL to the user's avatar image (nullable)
    :ivar confirmed: Email confirmation status
    :ivar role: User role — "user" or "admin" (default: "user")
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(String, default="user")


class Contact(Base):
    """
    Contact model representing a user's contact entry.

    :ivar id: Primary key identifier
    :ivar first_name: Contact's first name (max 50 characters)
    :ivar last_name: Contact's last name (max 50 characters)
    :ivar email: Contact's email address (unique, indexed)
    :ivar phone: Contact's phone number (max 15 characters)
    :ivar birthday: Contact's date of birth
    :ivar user_id: Foreign key referencing the owning user
    :ivar user: Relationship to the owning User
    """

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(15))
    birthday: Mapped[date] = mapped_column(Date)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")
