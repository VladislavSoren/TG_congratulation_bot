from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, Integer, UniqueConstraint, Boolean, TIMESTAMP, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from .base import Base

# Base = declarative_base()


class User(Base):
    surname: Mapped[str] = mapped_column(String(50), nullable=False, unique=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=False)
    otchestvo: Mapped[str] = mapped_column(String(50), nullable=False, unique=False)
    birthday: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, unique=False)

    # region_id: Mapped[int] = mapped_column(ForeignKey("region.id"))
    # creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    # # roles_target_audience  # NO REALISATION (#SPEAK)
    #
    # # relationships
    # region = relationship("Region", back_populates="event")
    # creator = relationship("User", back_populates="event")
    # speaker = relationship("EventSpeaker", back_populates="event")
    # visitor = relationship("EventVisitor", back_populates="event")


# Создание подключения к базе данных
engine = create_engine('sqlite+aiosqlite:///./test.db')

# class UserSubscriber(Base):
#     event_id: Mapped[int] = mapped_column(ForeignKey("event.id"), nullable=True)
#     speaker_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
#
#     # additional properties
#     __table_args__ = (UniqueConstraint("event_id", "speaker_id", name="unique_event_speaker_unit"),)
#
#     # relationships
#     event = relationship("Event", back_populates="speaker")
#     speaker = relationship("User", back_populates="event_speaker")
