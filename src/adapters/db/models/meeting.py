from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.db.models.base import Base, TimestampMixin
from src.core.enums import MeetingLevel, MeetingStatus


class Meeting(Base, TimestampMixin):
    __tablename__ = "meetings"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    template_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    project_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    level: Mapped[MeetingLevel] = mapped_column(default=MeetingLevel.OPERATIONAL, nullable=False)
    status: Mapped[MeetingStatus] = mapped_column(
        default=MeetingStatus.PREPARATION, nullable=False
    )
    content_markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="meeting", lazy="selectin", cascade="all, delete-orphan"
    )
    participants: Mapped[List["Participant"]] = relationship(
        "Participant", back_populates="meeting", lazy="selectin", cascade="all, delete-orphan"
    )
    agenda_items: Mapped[List["AgendaItem"]] = relationship(
        "AgendaItem", back_populates="meeting", lazy="selectin", cascade="all, delete-orphan"
    )
    notebook_links: Mapped[List["MeetingNotebook"]] = relationship(
        "MeetingNotebook", back_populates="meeting", lazy="selectin", cascade="all, delete-orphan"
    )