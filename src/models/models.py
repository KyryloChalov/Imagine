from datetime import datetime, date
import enum
import uuid
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, func, extract, Enum, ForeignKey, Boolean
from sqlalchemy.orm import column_property
from sqlalchemy.sql.sqltypes import Date, DateTime
from sqlalchemy_utils import EmailType
from fastapi_users_db_sqlalchemy import generics
from sqlalchemy.ext.hybrid import hybrid_property

# PhoneNumberType


from src.database.db import Base

class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    surname: Mapped[str] =  mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(EmailType, nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(12))
    birthday: Mapped[date] = mapped_column(Date)
    info: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    b_date = column_property(func.to_date(func.concat(datetime.today().year, '-', extract('month', birthday), '-', extract('day', birthday)), 'YYYY-MM-DD'))
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), nullable=True)
    user: Mapped["User"] = relationship("User", backref="contacts", lazy="joined")


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(generics.GUID(), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    role: Mapped[Enum] = mapped_column('role', Enum(Role), default=Role.user, nullable=True)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)