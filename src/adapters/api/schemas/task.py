from datetime import datetime
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


WorkflowStage = Literal["to_do", "in_progress", "escalated", "completed"]
RaciRole = Literal["R", "A", "C", "I"]


class RaciAssignmentCreate(BaseModel):
    user_id: UUID
    role: RaciRole


class RaciAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    role: str
    name: Optional[str] = None


class TaskCreate(BaseModel):
    meeting_id: UUID
    description: str = Field(min_length=1, max_length=2000)
    organization_links: list[UUID] = []


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    task_id: UUID
    task_number: str
    description: str
    workflow_stage: WorkflowStage
    raci_valid: bool = False
    is_ai_processed: bool = True
    planned_start: Optional[datetime] = None
    deadline: Optional[datetime] = None
    created_at: datetime


class TaskDetailResponse(TaskResponse):
    raci_assignments: list[RaciAssignmentResponse] = []


class RaciUpdateRequest(BaseModel):
    assignments: list[RaciAssignmentCreate]


class RaciResponse(BaseModel):
    task_id: UUID
    assignments: list[RaciAssignmentResponse]
    is_valid: bool
    errors: list[str] = []


class RaciValidationErrorResponse(BaseModel):
    error: Literal["RACI_VALIDATION_FAILED"] = "RACI_VALIDATION_FAILED"
    message: str
    is_valid: bool = False


class EscalateRequest(BaseModel):
    target_meeting_type: str
    reason: str


class EscalateResponse(BaseModel):
    source_task: TaskResponse
    destination_task: TaskResponse


class DependencyResponse(BaseModel):
    task_id: UUID
    graph_edges: dict[str, Optional[UUID]]