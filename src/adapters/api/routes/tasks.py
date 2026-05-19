from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.api.schemas.task import (
    DependencyResponse,
    EscalateRequest,
    EscalateResponse,
    RaciResponse,
    RaciUpdateRequest,
    RaciValidationErrorResponse,
    TaskCreate,
    TaskResponse,
)
from src.adapters.services import raci_service, task_service
from src.adapters.db.models import Task
from src.core.enums import RaciRole
from src.infrastructure.database import get_async_session
from src.infrastructure.dependencies import require_role, require_user

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


def _task_to_response(t: Task) -> TaskResponse:
    a_count = sum(1 for r in t.raci_assignments if r.role == RaciRole.A)
    return TaskResponse(
        task_id=t.id,
        task_number=t.task_number,
        description=t.description,
        workflow_stage=t.workflow_stage.value,
        raci_valid=(a_count == 1),
        is_ai_processed=t.is_ai_processed,
        planned_start=t.planned_start,
        deadline=t.deadline,
        created_at=t.created_at,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_role("secretary", "chairman", "admin")),
):
    task = await task_service.create_task(
        session,
        meeting_id=body.meeting_id,
        description=body.description,
        organization_ids=body.organization_links if body.organization_links else None,
    )
    return _task_to_response(task)


@router.get("/{task_id}/raci", response_model=RaciResponse)
async def get_raci(
    task_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_user),
):
    svc = raci_service.RaciService(session)
    try:
        return await svc.get_assignments(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.put("/{task_id}/raci", response_model=RaciResponse)
async def update_raci(
    task_id: UUID,
    body: RaciUpdateRequest,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_role("chairman", "admin")),
):
    svc = raci_service.RaciService(session)

    a_assignments = [a for a in body.assignments if a.role == "A"]
    if len(a_assignments) > 1:
        users = ", ".join(str(a.user_id)[:8] for a in a_assignments)
        raise HTTPException(
            status_code=422,
            detail={
                "error": "RACI_VALIDATION_FAILED",
                "message": (
                    f"Критическая ошибка: Обнаружено более одной роли "
                    f"'Accountable (A)' на задачу. Нарушен UNIQUE CONSTRAINT. "
                    f"Назначено {len(a_assignments)} пользователей: {users}."
                ),
                "is_valid": False,
            },
        )

    if len(a_assignments) == 0:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "RACI_VALIDATION_FAILED",
                "message": "Отсутствует роль 'Accountable (A)' на задачу.",
                "is_valid": False,
            },
        )

    assignments_data = [{"user_id": a.user_id, "role": a.role} for a in body.assignments]
    try:
        return await svc.update_assignments(
            task_id,
            assignments_data,
            auto_correct=False,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/escalate", response_model=EscalateResponse)
async def escalate(
    task_id: UUID,
    body: EscalateRequest,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_role("chairman", "admin")),
):
    try:
        source, dest = await task_service.escalate_task(
            session,
            task_id=task_id,
            target_meeting_type=body.target_meeting_type,
            reason=body.reason,
        )
        return EscalateResponse(
            source_task=_task_to_response(source),
            destination_task=_task_to_response(dest),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}/dependencies", response_model=DependencyResponse)
async def get_dependencies(
    task_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_user),
):
    try:
        edges = await task_service.get_task_dependencies(session, task_id)
        return DependencyResponse(task_id=task_id, graph_edges=edges)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")