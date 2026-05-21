from datetime import date
from uuid import UUID, uuid4
from typing import Optional

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.db.models.base import Base, TimestampMixin


class Contract(Base, TimestampMixin):
    __tablename__ = "contracts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    client_org_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    contractor_org_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    meeting_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("meetings.id", ondelete="SET NULL"), nullable=True
    )

    client = relationship("Organization", foreign_keys=[client_org_id], lazy="selectin")
    contractor = relationship("Organization", foreign_keys=[contractor_org_id], lazy="selectin")
    meeting = relationship("Meeting", backref="contracts", lazy="selectin")
