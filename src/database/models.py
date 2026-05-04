from sqlalchemy import String, func
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase

from datetime import date
from sqlalchemy import Date


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(15))
    birthday: Mapped[date] = mapped_column(Date)
