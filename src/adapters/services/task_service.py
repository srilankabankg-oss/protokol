from datetime import datetime, UTC
from uuid import UUID, uuid4
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.db.models import Task, Meeting, RaciAssignment, TaskOrganization
from src.core.enums import MeetingLevel, MeetingStatus, WorkflowStage, RaciRole


async def _generate_task_number(
    session: AsyncSession, meeting_id: UUID, project_id: Optional[UUID] = None
) -> str:
    from sqlalchemy import func

    result = await session.execute(select(func.count()).where(Task.meeting_id == meeting_id))
    seq = (result.scalar() or 0) + 1

    prefix = "KDD-OPR"
    meeting = await session.get(Meeting, meeting_id)
    if meeting:
        level_map = {
            MeetingLevel.STRATEGIC: "STR",
            MeetingLevel.COORDINATION: "CRD",
            MeetingLevel.OPERATIONAL: "OPR",
            MeetingLevel.SITUATIONAL: "SIT",
        }
        prefix = f"KDD-{level_map.get(meeting.level, 'OPR')}"

    return f"{prefix}-{seq:03d}"


async def create_task(
    session: AsyncSession,
    meeting_id: UUID,
    description: str,
    organization_ids: list[UUID] = None,
) -> Task:
    task_number = await _generate_task_number(session, meeting_id)

    task = Task(
        id=uuid4(),
        meeting_id=meeting_id,
        task_number=task_number,
        description=description,
        workflow_stage=WorkflowStage.TO_DO,
    )
    session.add(task)

    if organization_ids:
        for org_id in organization_ids:
            link = TaskOrganization(
                id=uuid4(),
                task_id=task.id,
                organization_id=org_id,
            )
            session.add(link)

    await session.flush()
    return task


async def escalate_task(
    session: AsyncSession,
    task_id: UUID,
    target_meeting_type: str,
    reason: str,
) -> tuple[Task, Task]:
    source_task = await session.get(Task, task_id)
    if source_task is None:
        raise ValueError("Source task not found")

    target_level_map = {
        "Координационное": MeetingLevel.COORDINATION,
        "Стратегическое": MeetingLevel.STRATEGIC,
        "coordination": MeetingLevel.COORDINATION,
        "strategic": MeetingLevel.STRATEGIC,
    }
    target_level = target_level_map.get(target_meeting_type, MeetingLevel.COORDINATION)

    result = await session.execute(
        select(Meeting)
        .where(Meeting.level == target_level, Meeting.status != MeetingStatus.APPROVED)
        .order_by(Meeting.created_at.desc())
        .limit(1)
    )
    target_meeting = result.scalar_one_or_none()

    if target_meeting is None:
        target_meeting = Meeting(
            id=uuid4(),
            title=f"Эскалация: {source_task.description[:100]}",
            level=target_level,
            status=MeetingStatus.PREPARATION,
            date=datetime.now(UTC),
        )
        session.add(target_meeting)

    src_accountables = [a for a in source_task.raci_assignments if a.role == RaciRole.A]

    source_task.workflow_stage = WorkflowStage.ESCALATED

    dest_task_number = await _generate_task_number(session, target_meeting.id)
    dest_task = Task(
        id=uuid4(),
        meeting_id=target_meeting.id,
        task_number=dest_task_number,
        description=source_task.description,
        workflow_stage=WorkflowStage.TO_DO,
        parent_task_id=source_task.id,
    )
    session.add(dest_task)

    for acc in src_accountables:
        raci = RaciAssignment(
            id=uuid4(),
            task_id=dest_task.id,
            user_id=acc.user_id,
            role=RaciRole.R,
            note="Бывший Accountable готовит доклад",
        )
        session.add(raci)

    await session.flush()
    return source_task, dest_task


async def get_task_dependencies(session: AsyncSession, task_id: UUID) -> dict:
    task = await session.get(Task, task_id)
    if task is None:
        raise ValueError("Task not found")

    return {
        "previous_task_id": task.parent_task_id,
        "next_task_id": None,
    }