from uuid import UUID, uuid4
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.db.models.base import Base
from src.core.enums import ParticipantRole


class Participant(Base):
    __tablename__ = "meeting_participants"
    __table_args__ = (UniqueConstraint("meeting_id", "user_id"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    meeting_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    person_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("people.id", ondelete="CASCADE"), nullable=True
    )
    role_in_meeting: Mapped[ParticipantRole] = mapped_column(
        default=ParticipantRole.PARTICIPANT, nullable=False
    )
    is_present: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", lazy="selectin")
    person = relationship("Person", lazy="selectin")
