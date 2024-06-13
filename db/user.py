from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, Integer, UniqueConstraint, Boolean, TIMESTAMP, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from .models import Base


# Base = declarative_base()


class User(Base):
    surname: Mapped[str] = mapped_column(String(50), nullable=False, unique=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=False)
    otchestvo: Mapped[str] = mapped_column(String(50), nullable=False, unique=False)
    birthday: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, unique=False)

    # relationships
    user = relationship("UserSubscriber", back_populates="user")
    subscriber = relationship("UserSubscriber", back_populates="subscriber")


class UserSubscriber(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    subscriber_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)

    # additional properties
    __table_args__ = (UniqueConstraint("user_id", "subscriber_id", name="unique_user_subscriber_unit"),)

    # relationships
    user = relationship("User", back_populates="user")
    subscriber = relationship("User", back_populates="subscriber")


# Создание подключения к базе данных
engine = create_engine('sqlite+aiosqlite:///./test.db')
