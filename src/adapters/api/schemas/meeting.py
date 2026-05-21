from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


MeetingLevel = Literal["strategic", "coordination", "operational", "situational"]
MeetingStatus = Literal["preparation", "in_progress", "on_approval", "approved"]

_SUSPICIOUS_PATTERN = re.compile(
    r"<script|<iframe|<img|javascript:|onerror=|onload=|"
    r"DROP\s+TABLE|DELETE\s+FROM|INSERT\s+INTO|UNION\s+SELECT",
    re.IGNORECASE,
)


class AgendaItemCreate(BaseModel):
    position: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=500)


class AgendaItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    agenda_id: UUID
    title: str
    position: int
    is_completed: bool


class ParticipantCreate(BaseModel):
    user_id: UUID
    role_in_meeting: Literal["chairman", "secretary", "participant"] = "participant"


class ParticipantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    name: str
    role: str
    is_present: bool


class MeetingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    template_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    level: MeetingLevel = "operational"
    agenda_items: list[AgendaItemCreate] = []

    @field_validator("title")
    @classmethod
    def reject_suspicious_input(cls, v: str) -> str:
        if _SUSPICIOUS_PATTERN.search(v):
            raise ValueError("Title contains invalid characters or patterns")
        return v


class MeetingCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    meeting_id: UUID
    status: MeetingStatus
    imported_legacy_tasks_count: int = 0
    celery_task_id: Optional[str] = None


class MeetingListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    meeting_id: UUID
    title: str
    level: str
    status: str
    notebook_path: Optional[str] = None
    date: Optional[datetime] = None
    updated_at: datetime


class MeetingWorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    meeting_id: UUID
    title: str
    breadcrumbs: list[str]
    status: MeetingStatus
    content_markdown: Optional[str] = None
    participants: list[ParticipantResponse]
    agenda: list[AgendaItemResponse]


class ContentUpdateRequest(BaseModel):
    content_markdown: str


class ContentUpdateResponse(BaseModel):
    status: Literal["success"] = "success"
    version: int
    updated_at: datetime


class StatusTransitionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    meeting_id: UUID
    status: MeetingStatus
    transition_timestamp: datetime


class ApproveResponse(StatusTransitionResponse):
    pdf_export_job_id: Optional[str] = None
    xlsx_export_job_id: Optional[str] = None