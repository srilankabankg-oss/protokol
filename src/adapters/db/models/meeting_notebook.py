from uuid import UUID

from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.db.models.base import Base


class MeetingNotebook(Base):
    __tablename__ = "meeting_notebooks"
    __table_args__ = (PrimaryKeyConstraint("meeting_id", "notebook_id"),)

    meeting_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    )
    notebook_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("notebooks.id", ondelete="CASCADE"),
        nullable=False,
    )

    meeting = relationship("Meeting", back_populates="notebook_links")
    notebook = relationship("Notebook", back_populates="meeting_links")