from datetime import datetime, UTC
from uuid import UUID, uuid4
from typing import Optional, Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.adapters.db.models import Meeting, Participant, AgendaItem, Task, User
from src.core.enums import MeetingLevel, MeetingStatus, ParticipantRole, WorkflowStage


async def list_meetings(
    session: AsyncSession,
    project_id: Optional[UUID] = None,
    organization_id: Optional[UUID] = None,
    level: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Meeting]:
    query = select(Meeting).options(selectinload(Meeting.tasks))
    if project_id:
        query = query.where(Meeting.project_id == project_id)
    if level:
        query = query.where(Meeting.level == level)
    if organization_id:
        query = query.where(
            Meeting.tasks.any(
                Task.organization_links.any(organization_id=organization_id)
            )
        )
    query = query.order_by(Meeting.updated_at.desc()).offset(offset).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_meeting_workspace(session: AsyncSession, meeting_id: UUID) -> Optional[Meeting]:
    result = await session.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.participants).joinedload(Participant.user),
            selectinload(Meeting.agenda_items),
            selectinload(Meeting.tasks),
        )
        .where(Meeting.id == meeting_id)
    )
    return result.scalar_one_or_none()


async def create_meeting(
    session: AsyncSession,
    title: str,
    level: MeetingLevel,
    template_id: Optional[UUID] = None,
    project_id: Optional[UUID] = None,
    agenda_data: list[dict] = None,
) -> tuple[Meeting, int]:
    meeting = Meeting(
        id=uuid4(),
        title=title,
        template_id=template_id,
        project_id=project_id,
        level=level,
        status=MeetingStatus.PREPARATION,
        date=datetime.now(UTC),
    )
    session.add(meeting)

    if agenda_data:
        for item in agenda_data:
            agenda = AgendaItem(
                id=uuid4(),
                meeting_id=meeting.id,
                position=item["position"],
                title=item["title"],
            )
            session.add(agenda)

    imported_count = await _import_legacy_tasks(session, meeting.id, project_id)
    try:
        from src.adapters.services.protocol_parser import parse_notes_to_protocol
        import asyncio
        protocol = await parse_notes_to_protocol(content_markdown)
        if any(protocol.values()):
            meeting.protocol_data = protocol
    except Exception:
        pass

    await session.flush()

    return meeting, imported_count


async def _import_legacy_tasks(
    session: AsyncSession, meeting_id: UUID, project_id: Optional[UUID]
) -> int:
    stmt = select(Task).where(
        Task.workflow_stage.in_([WorkflowStage.TO_DO, WorkflowStage.IN_PROGRESS]),
        Task.meeting_id != meeting_id,
    )
    if project_id:
        stmt = stmt.where(Task.meeting.has(Meeting.project_id == project_id))

    result = await session.execute(stmt)
    legacy_tasks = result.scalars().all()

    count = 0
    for task in legacy_tasks:
        imported = Task(
            id=uuid4(),
            meeting_id=meeting_id,
            task_number=task.task_number,
            description=task.description,
            workflow_stage=task.workflow_stage,
            parent_task_id=task.id,
        )
        session.add(imported)
        count += 1

    return count


async def update_meeting_content(
    session: AsyncSession, meeting_id: UUID, content_markdown: str, expected_version: Optional[int] = None
) -> tuple[int, datetime]:
    meeting = await session.get(Meeting, meeting_id)
    if meeting is None:
        raise ValueError("Meeting not found")
    if meeting.status == MeetingStatus.APPROVED:
        raise ValueError("Approved meetings cannot be modified")
    if expected_version is not None and meeting.version != expected_version:
        raise ValueError(f"Version conflict: expected {expected_version}, current {meeting.version}")

    meeting.content_markdown = content_markdown
    meeting.version += 1
    meeting.updated_at = datetime.now(UTC)
    try:
        from src.adapters.services.protocol_parser import parse_notes_to_protocol
        import asyncio
        protocol = await parse_notes_to_protocol(content_markdown)
        if any(protocol.values()):
            meeting.protocol_data = protocol
    except Exception:
        pass

    await session.flush()
    return meeting.version, meeting.updated_at


async def start_work(session: AsyncSession, meeting_id: UUID) -> Meeting:
    meeting = await session.get(Meeting, meeting_id)
    if meeting is None:
        raise ValueError("Meeting not found")
    if meeting.status != MeetingStatus.PREPARATION:
        raise ValueError(f"Cannot start work in status: {meeting.status.value}")

    meeting.status = MeetingStatus.IN_PROGRESS
    meeting.updated_at = datetime.now(UTC)
    try:
        from src.adapters.services.protocol_parser import parse_notes_to_protocol
        import asyncio
        protocol = await parse_notes_to_protocol(content_markdown)
        if any(protocol.values()):
            meeting.protocol_data = protocol
    except Exception:
        pass

    await session.flush()
    await session.refresh(meeting)
    return meeting


async def finalize_meeting(session: AsyncSession, meeting_id: UUID) -> Meeting:
    meeting = await session.get(Meeting, meeting_id)
    if meeting is None:
        raise ValueError("Meeting not found")
    if meeting.status != MeetingStatus.IN_PROGRESS:
        raise ValueError(f"Cannot finalize meeting in status: {meeting.status.value}")

    meeting.status = MeetingStatus.ON_APPROVAL
    meeting.updated_at = datetime.now(UTC)
    try:
        from src.adapters.services.protocol_parser import parse_notes_to_protocol
        import asyncio
        protocol = await parse_notes_to_protocol(content_markdown)
        if any(protocol.values()):
            meeting.protocol_data = protocol
    except Exception:
        pass

    await session.flush()
    await session.refresh(meeting)
    return meeting


async def approve_meeting(session: AsyncSession, meeting_id: UUID) -> Meeting:
    meeting = await session.get(Meeting, meeting_id)
    if meeting is None:
        raise ValueError("Meeting not found")
    if meeting.status != MeetingStatus.ON_APPROVAL:
        raise ValueError(f"Cannot approve meeting in status: {meeting.status.value}")

    meeting.status = MeetingStatus.APPROVED
    meeting.updated_at = datetime.now(UTC)
    try:
        from src.adapters.services.protocol_parser import parse_notes_to_protocol
        import asyncio
        protocol = await parse_notes_to_protocol(content_markdown)
        if any(protocol.values()):
            meeting.protocol_data = protocol
    except Exception:
        pass

    await session.flush()
    await session.refresh(meeting)
    return meeting