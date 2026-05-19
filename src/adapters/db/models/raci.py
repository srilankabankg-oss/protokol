from uuid import UUID, uuid4
from typing import Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.db.models.base import Base
from src.core.enums import RaciRole


class RaciAssignment(Base):
    __tablename__ = "raci_assignments"
    __table_args__ = (UniqueConstraint("task_id", "user_id", "role"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    task_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[RaciRole] = mapped_column(nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    task = relationship("Task", back_populates="raci_assignments")
    user = relationship("User", back_populates="raci_assignments")