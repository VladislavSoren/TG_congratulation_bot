from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    surname: Mapped[str] = mapped_column(String(50), nullable=False, unique=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=False)
    otchestvo: Mapped[str] = mapped_column(String(50), nullable=False, unique=False)
    birthday: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, unique=False)

    # relationships
    subscriber = relationship("UserSubscriber", back_populates="user")


class Subscriber(Base):
    __tablename__ = 'subscriber'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)

    # additional properties
    __table_args__ = (UniqueConstraint("user_id"),)

    # relationships
    user = relationship("UserSubscriber", back_populates="subscriber")


class UserSubscriber(Base):
    __tablename__ = 'user_subscriber'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    subscriber_id: Mapped[int] = mapped_column(ForeignKey("subscriber.id"), nullable=True)

    # additional properties
    __table_args__ = (UniqueConstraint("user_id", "subscriber_id", name="unique_user_subscriber_unit"),)

    # relationships
    user = relationship("User", back_populates="subscriber")
    subscriber = relationship("Subscriber", back_populates="user")
