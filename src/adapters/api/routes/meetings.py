from datetime import datetime
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.api.schemas.meeting import (
    MeetingCreate,
    MeetingCreateResponse,
    MeetingListItem,
    MeetingWorkspaceResponse,
    ContentUpdateRequest,
    ContentUpdateResponse,
    StatusTransitionResponse,
    ApproveResponse,
)
from src.adapters.services import meeting_service
from src.adapters.services.export_service import generate_pdf, generate_xlsx
from src.core.enums import MeetingLevel
from src.infrastructure.celery_app import export_pdf_task, export_xlsx_task, send_notifications_task
from src.infrastructure.database import get_async_session
from src.infrastructure.dependencies import require_user, require_role

router = APIRouter(prefix="/api/v1/meetings", tags=["meetings"])


@router.get("", response_model=list[MeetingListItem])
async def list_meetings(
    project_id: Optional[UUID] = Query(default=None),
    organization_id: Optional[UUID] = Query(default=None),
    level: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_user),
):
    meetings = await meeting_service.list_meetings(
        session, project_id=project_id, organization_id=organization_id,
        level=level, limit=limit, offset=offset,
    )
    return [
        MeetingListItem(
            id=m.id, title=m.title, level=m.level.value, status=m.status.value,
            notebook_path=None, date=m.date, updated_at=m.updated_at,
        )
        for m in meetings
    ]


@router.post("", response_model=MeetingCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_new_meeting(
    body: MeetingCreate,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_role("secretary", "admin")),
):
    agenda_data = [{"position": a.position, "title": a.title} for a in body.agenda_items]
    meeting, imported_count = await meeting_service.create_meeting(
        session, title=body.title, level=MeetingLevel(body.level),
        template_id=body.template_id, project_id=body.project_id,
        agenda_data=agenda_data,
    )
    celery_task = send_notifications_task.delay(str(meeting.id), [])
    return MeetingCreateResponse(
        id=meeting.id, status=meeting.status.value,
        imported_legacy_tasks_count=imported_count, celery_task_id=celery_task.id,
    )


@router.get("/{meeting_id}/workspace", response_model=MeetingWorkspaceResponse)
async def get_workspace(
    meeting_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_user),
):
    meeting = await meeting_service.get_meeting_workspace(session, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    breadcrumbs = ["Книга добрых дел", meeting.title]
    participants = []
    for p in meeting.participants:
        participants.append(dict(user_id=p.user_id, name=p.user.name if p.user else "Unknown",
                                  role=p.role_in_meeting.value, is_present=p.is_present))
    agenda = []
    for a in meeting.agenda_items:
        agenda.append(dict(id=a.id, title=a.title, position=a.position, is_completed=a.is_completed))
    return MeetingWorkspaceResponse(
        id=meeting.id, breadcrumbs=breadcrumbs, status=meeting.status.value,
        content_markdown=meeting.content_markdown,
        participants=participants, agenda=agenda,
    )


@router.patch("/{meeting_id}/content", response_model=ContentUpdateResponse)
async def update_content(
    meeting_id: UUID, body: ContentUpdateRequest,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_role("secretary", "admin")),
):
    try:
        version, updated_at = await meeting_service.update_meeting_content(
            session, meeting_id, body.content_markdown)
        return ContentUpdateResponse(version=version, updated_at=updated_at)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{meeting_id}/finalize", response_model=StatusTransitionResponse)
async def finalize(
    meeting_id: UUID, session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_role("secretary", "admin")),
):
    try:
        meeting = await meeting_service.finalize_meeting(session, meeting_id)
        return StatusTransitionResponse(
            id=meeting.id, status=meeting.status.value,
            transition_timestamp=meeting.updated_at)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{meeting_id}/approve", response_model=ApproveResponse)
async def approve(
    meeting_id: UUID, session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_role("chairman", "admin")),
):
    try:
        meeting = await meeting_service.approve_meeting(session, meeting_id)
        pdf_job = export_pdf_task.delay(str(meeting.id))
        xlsx_job = export_xlsx_task.delay(str(meeting.id))
        return ApproveResponse(
            id=meeting.id, status=meeting.status.value,
            transition_timestamp=meeting.updated_at,
            pdf_export_job_id=pdf_job.id, xlsx_export_job_id=xlsx_job.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{meeting_id}/export/pdf")
async def download_pdf(
    meeting_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_user),
):
    from fastapi.responses import FileResponse
    from sqlalchemy import select as sa_select
    from sqlalchemy.orm import selectinload as sa_selectinload

    result = await session.execute(
        sa_select(Meeting)
        .options(sa_selectinload(Meeting.tasks).sa_selectinload(Task.raci_assignments))
        .where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    filepath = generate_pdf(meeting, list(meeting.tasks))
    return FileResponse(filepath, filename=f"protocol_{meeting_id}.pdf",
                        media_type="application/pdf")


@router.get("/{meeting_id}/export/xlsx")
async def download_xlsx(
    meeting_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    _current_user=Depends(require_user),
):
    from fastapi.responses import FileResponse

    result = await session.execute(
        sa_select(Meeting)
        .options(sa_selectinload(Meeting.tasks).sa_selectinload(Task.raci_assignments))
        .where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    filepath = generate_xlsx(meeting, list(meeting.tasks))
    return FileResponse(filepath, filename=f"protocol_{meeting_id}.xlsx",
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")