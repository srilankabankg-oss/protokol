from uuid import UUID, uuid4
from typing import Optional, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.db.models.base import Base, TimestampMixin


class Notebook(Base, TimestampMixin):
    __tablename__ = "notebooks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("notebooks.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(1000), nullable=False)

    parent = relationship("Notebook", remote_side=[id], backref="children")
    meeting_links: Mapped[List["MeetingNotebook"]] = relationship(
        "MeetingNotebook", back_populates="notebook", lazy="selectin", cascade="all, delete-orphan"
    )