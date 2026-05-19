from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.api.schemas.task import (
    TaskCreate, TaskResponse, EscalateRequest, EscalateResponse,
    DependencyResponse, RaciUpdateRequest, RaciResponse, RaciValidationErrorResponse,
)
from src.adapters import services as task_service_import
from src.adapters.db.models import Task, RaciAssignment
from src.core.enums import RaciRole, WorkflowStage
from src.infrastructure.database import get_async_session
from src.infrastructure.dependencies import require_user, require_role

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


import src.adapters.services.task_service as task_service


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    body: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_role("secretary", "chairman", "admin")),
):
    task = await task_service.create_task(
        session, meeting_id=body.meeting_id, description=body.description,
        organization_ids=body.organization_links or [],
    )
    a_count = sum(1 for r in task.raci_assignments if r.role == RaciRole.A)
    return TaskResponse(
        id=task.id, task_number=task.task_number, description=task.description,
        workflow_stage=task.workflow_stage.value, raci_valid=(a_count == 1),
        is_ai_processed=task.is_ai_processed, planned_start=task.planned_start,
        deadline=task.deadline, created_at=task.created_at,
    )


@router.get("/{task_id}/raci", response_model=RaciResponse)
async def get_raci(
    task_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_user),
):
    result = await session.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    assignments = []
    for a in task.raci_assignments:
        assignments.append(dict(user_id=a.user_id, role=a.role.value))
    a_count = sum(1 for a in task.raci_assignments if a.role == RaciRole.A)
    return RaciResponse(task_id=task.id, assignments=assignments,
                        is_valid=(a_count == 1), errors=[])


@router.put("/{task_id}/raci", response_model=RaciResponse)
async def update_raci(
    task_id: UUID, body: RaciUpdateRequest,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_role("chairman", "admin")),
):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    a_count = sum(1 for a in body.assignments if a.role == "A")
    if a_count != 1:
        msg = ("Критическая ошибка: Обнаружено более одной роли 'Accountable (A)' на задачу."
               if a_count > 1 else "Отсутствует роль 'Accountable (A)'")
        return RaciValidationErrorResponse(error="RACI_VALIDATION_FAILED",
                                           message=msg, is_valid=False)

    await session.execute(delete(RaciAssignment).where(RaciAssignment.task_id == task_id))
    for a in body.assignments:
        ra = RaciAssignment(id=uuid4(), task_id=task_id, user_id=a.user_id,
                            role=RaciRole(a.role))
        session.add(ra)
    await session.flush()
    return RaciResponse(
        task_id=task_id,
        assignments=[dict(user_id=a.user_id, role=a.role) for a in body.assignments],
        is_valid=True, errors=[],
    )


@router.post("/{task_id}/escalate", response_model=EscalateResponse)
async def escalate(
    task_id: UUID, body: EscalateRequest,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_role("chairman", "admin")),
):
    try:
        source, dest = await task_service.escalate_task(
            session, task_id=task_id,
            target_meeting_type=body.target_meeting_type, reason=body.reason,
        )
        return EscalateResponse(
            source_task=TaskResponse(id=source.id, task_number=source.task_number,
                                     description=source.description,
                                     workflow_stage=source.workflow_stage.value,
                                     raci_valid=True, is_ai_processed=source.is_ai_processed,
                                     planned_start=source.planned_start,
                                     deadline=source.deadline, created_at=source.created_at),
            destination_task=TaskResponse(
                id=dest.id, task_number=dest.task_number,
                description=dest.description,
                workflow_stage=dest.workflow_stage.value,
                raci_valid=True, is_ai_processed=dest.is_ai_processed,
                planned_start=dest.planned_start, deadline=dest.deadline,
                created_at=dest.created_at,
            ),
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