from datetime import date, datetime
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


OrgRole = Literal["client", "general_contractor", "subcontractor", "supplier"]


class OrganizationBase(BaseModel):
    name: str = Field(max_length=255)
    inn: Optional[str] = Field(default=None, max_length=12)
    profile: Optional[str] = None
    role: Optional[OrgRole] = None


class OrganizationCreate(OrganizationBase):
    parent_id: Optional[UUID] = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    inn: Optional[str] = None
    profile: Optional[str] = None
    role: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: bool = True


class PersonCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    job_title: Optional[str] = Field(default=None, max_length=255)
    org_id: Optional[UUID] = None


class PersonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    full_name: str
    job_title: Optional[str] = None
    org_id: Optional[UUID] = None


class ContractCreate(BaseModel):
    subject: str = Field(max_length=500)
    end_date: Optional[date] = None
    client_org_id: UUID
    contractor_org_id: UUID
    meeting_id: Optional[UUID] = None


class ContractResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    subject: str
    end_date: Optional[date] = None
    client_org_id: UUID
    contractor_org_id: UUID
    meeting_id: Optional[UUID] = None
