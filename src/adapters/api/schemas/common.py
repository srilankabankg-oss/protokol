from datetime import datetime
from typing import Optional, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int


class SuccessResponse(BaseModel):
    status: str = "success"
    message: Optional[str] = None