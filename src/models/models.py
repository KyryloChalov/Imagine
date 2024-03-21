from datetime import datetime, date
import enum
import uuid
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, func, Table, extract, Enum, ForeignKey, Boolean
from sqlalchemy.orm import column_property
from sqlalchemy.sql.sqltypes import Date, DateTime
from sqlalchemy_utils import EmailType
from fastapi_users_db_sqlalchemy import generics
from sqlalchemy.ext.hybrid import hybrid_property


from src.database.db import Base

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    
photo_m2m_tag = Table(
    "photo_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("photo_id", Integer, ForeignKey("photos.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)

class Photo(Base):
    __tablename__ = "photos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    path: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] =  mapped_column(String(250), nullable=False)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    path_tranform: Mapped[str] = mapped_column(String(250))
    # b_date = column_property(func.to_date(func.concat(datetime.today().year, '-', extract('month', birthday), '-', extract('day', birthday)), 'YYYY-MM-DD'))
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), nullable=True)
    user: Mapped["User"] = relationship("User", backref="photos", lazy="joined")
    tags = relationship("Tag", secondary=photo_m2m_tag, backref="photos")
    
    
class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opinion: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id'), nullable=True)
    user: Mapped["User"] = relationship("User", backref="comments", lazy="joined")
    photo_id: Mapped[int] = mapped_column(ForeignKey('photos.id'), nullable=True)
    photo: Mapped["Photo"] = relationship("Photo", backref="comments", lazy="joined")


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(generics.GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    role: Mapped[Enum] = mapped_column('role', Enum(Role), default=Role.user, nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    banned_at: Mapped[date] = mapped_column(Date, nullable=True)
    # avatar: Mapped[str] = mapped_column(String(255), nullable=True)