from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.adapters.db.models.base import Base, TimestampMixin
from src.core.enums import WorkflowStage


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    meeting_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    workflow_stage: Mapped[WorkflowStage] = mapped_column(
        default=WorkflowStage.TO_DO, nullable=False
    )
    is_ai_processed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    planned_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    parent_task_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    meeting = relationship("Meeting", back_populates="tasks")
    raci_assignments: Mapped[List["RaciAssignment"]] = relationship(
        "RaciAssignment", back_populates="task", lazy="selectin", cascade="all, delete-orphan"
    )
    organization_links: Mapped[List["TaskOrganization"]] = relationship(
        "TaskOrganization", back_populates="task", lazy="selectin", cascade="all, delete-orphan"
    )
    parent_task = relationship("Task", remote_side=[id], backref="child_tasks")