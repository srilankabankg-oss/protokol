from uuid import UUID, uuid4
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.adapters.db.models import Task, RaciAssignment, User
from src.core.enums import RaciRole


class RaciValidationError(Exception):
    pass


class RaciService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_assignments(self, task_id: UUID) -> dict:
        result = await self.session.execute(
            select(Task)
            .options(
                selectinload(Task.raci_assignments).selectinload(RaciAssignment.user)
            )
            .where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        if task is None:
            raise ValueError("Task not found")

        assignments = []
        for ra in task.raci_assignments:
            assignments.append({
                "user_id": ra.user_id,
                "role": ra.role.value,
                "name": ra.user.name if ra.user else f"User-{ra.user_id}",
            })

        validation = self._validate(assignments)
        return {
            "task_id": task.id,
            "assignments": assignments,
            "is_valid": validation["is_valid"],
            "errors": validation["errors"],
        }

    async def update_assignments(
        self,
        task_id: UUID,
        assignments_data: list[dict],
        auto_correct: bool = True,
    ) -> dict:
        task = await self.session.get(
            Task, task_id, options=[selectinload(Task.raci_assignments)]
        )
        if task is None:
            raise ValueError("Task not found")

        validation = self._validate(assignments_data)

        if auto_correct and not validation["is_valid"]:
            assignments_data = self._auto_correct_assignments(
                assignments_data, task_id
            )

        await self.session.execute(
            delete(RaciAssignment).where(RaciAssignment.task_id == task_id)
        )

        for a in assignments_data:
            ra = RaciAssignment(
                id=uuid4(),
                task_id=task_id,
                user_id=a["user_id"],
                role=RaciRole(a["role"]),
            )
            self.session.add(ra)

        await self.session.flush()

        return {
            "task_id": task_id,
            "assignments": [
                {"user_id": a["user_id"], "role": a["role"], "name": None}
                for a in assignments_data
            ],
            "is_valid": True,
            "errors": [],
        }

    def _validate(self, assignments: list[dict]) -> dict:
        a_assignments = [a for a in assignments if a.get("role") in ("A", RaciRole.A)]
        errors = []

        if len(a_assignments) == 0:
            errors.append("Отсутствует роль 'Accountable (A)' на задачу.")
        elif len(a_assignments) > 1:
            users = [str(a.get("user_id", "?"))[:8] for a in a_assignments]
            errors.append(
                f"Критическая ошибка: Обнаружено более одной роли 'Accountable (A)' "
                f"на задачу. Нарушен UNIQUE CONSTRAINT. Назначено: {len(a_assignments)} "
                f"Accountable ({', '.join(users)}...)."
            )

        return {
            "is_valid": len(a_assignments) == 1,
            "errors": errors,
        }

    def _auto_correct_assignments(self, assignments: list[dict], task_id: UUID) -> list[dict]:
        a_assignments = []
        other_assignments = []

        for a in assignments:
            if a.get("role") in ("A", RaciRole.A):
                a_assignments.append(a)
            else:
                other_assignments.append(a)

        if len(a_assignments) > 1:
            first_a = a_assignments[0]
            other_assignments.append(first_a)

            for extra in a_assignments[1:]:
                other_assignments.append({
                    "user_id": extra["user_id"],
                    "role": "R",
                })

        elif len(a_assignments) == 0:
            pass

        return other_assignments

    async def validate_raci_for_task(self, task_id: UUID) -> dict:
        task = await self.session.get(
            Task, task_id, options=[selectinload(Task.raci_assignments)]
        )
        if task is None:
            raise ValueError("Task not found")

        assignments = [
            {"user_id": ra.user_id, "role": ra.role.value}
            for ra in task.raci_assignments
        ]
        return self._validate(assignments)