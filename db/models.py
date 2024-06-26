from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    username_telegram: Mapped[str] = mapped_column(String(50), nullable=True)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    otchestvo: Mapped[str] = mapped_column(String(50), nullable=True)
    birthday: Mapped[datetime] = mapped_column(Date(), nullable=False)

    # relationships
    subscriber = relationship("UserSubscriber", back_populates="user")


class Subscriber(Base):
    __tablename__ = 'subscriber'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # additional properties
    __table_args__ = (UniqueConstraint("user_id"),)

    # relationships
    user = relationship("UserSubscriber", back_populates="subscriber")


class UserSubscriber(Base):
    __tablename__ = 'user_subscriber'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    subscriber_id: Mapped[int] = mapped_column(ForeignKey("subscriber.id"), nullable=False)

    # additional properties
    __table_args__ = (UniqueConstraint("user_id", "subscriber_id", name="unique_user_subscriber_unit"),)

    # relationships
    user = relationship("User", back_populates="subscriber")
    subscriber = relationship("Subscriber", back_populates="user")
