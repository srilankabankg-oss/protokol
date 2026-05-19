from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NotebookCreate(BaseModel):
    parent_id: Optional[UUID] = None
    name: str = Field(max_length=255)


class NotebookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    parent_id: Optional[UUID] = None
    name: str
    path: str
    created_at: datetime
    children: list["NotebookResponse"] = []