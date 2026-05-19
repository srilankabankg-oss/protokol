from datetime import datetime
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


MeetingLevel = Literal["strategic", "coordination", "operational", "situational"]
MeetingStatus = Literal["preparation", "in_progress", "on_approval", "approved"]


class AgendaItemCreate(BaseModel):
    position: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=500)


class AgendaItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    agenda_id: UUID = Field(alias="id")
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
    title: str = Field(max_length=500)
    template_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    level: MeetingLevel = "operational"
    agenda_items: list[AgendaItemCreate] = []


class MeetingCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    meeting_id: UUID = Field(alias="id")
    status: MeetingStatus
    imported_legacy_tasks_count: int = 0
    celery_task_id: Optional[str] = None


class MeetingListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    meeting_id: UUID = Field(alias="id")
    title: str
    level: str
    status: str
    notebook_path: Optional[str] = None
    date: Optional[datetime] = None
    updated_at: datetime


class MeetingWorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    meeting_id: UUID = Field(alias="id")
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

    meeting_id: UUID = Field(alias="id")
    status: MeetingStatus
    transition_timestamp: datetime


class ApproveResponse(StatusTransitionResponse):
    pdf_export_job_id: Optional[str] = None
    xlsx_export_job_id: Optional[str] = None