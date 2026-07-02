from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.task import Task, TaskCreate, TaskStatus, TaskUpdate


class TaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, payload: TaskCreate) -> Task:
        task = Task(**payload.model_dump())
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get(self, task_id: int) -> Task | None:
        return self.session.get(Task, task_id)

    def recent_activity(self, *, limit: int) -> list[Task]:
        id_statement = select(Task.id).order_by(Task.updated_at.desc()).limit(limit)
        task_ids = list(self.session.scalars(id_statement))
        tasks: list[Task] = []
        for task_id in task_ids:
            task = self.session.get(Task, task_id)
            if task is not None:
                tasks.append(task)
        return tasks

    def list_tasks(
        self,
        *,
        status: TaskStatus | None,
        owner: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[Task], int]:
        statement = select(Task)
        count_statement = select(func.count()).select_from(Task)

        if status is not None:
            statement = statement.where(Task.status == status)
            count_statement = count_statement.where(Task.status == status)
        if owner is not None:
            statement = statement.where(Task.owner == owner)
            count_statement = count_statement.where(Task.owner == owner)

        total = self.session.scalar(count_statement) or 0
        tasks = list(
            self.session.scalars(
                statement.order_by(Task.created_at.desc()).limit(limit).offset(offset)
            )
        )
        return tasks, total

    def search(self, *, query: str, limit: int, offset: int) -> tuple[list[Task], int]:
        pattern = f"%{query}%"
        filter_expression = or_(
            Task.title.ilike(pattern),
            Task.description.ilike(pattern),
            Task.owner.ilike(pattern),
        )
        count_statement = (
            select(func.count()).select_from(Task).where(filter_expression)
        )
        statement = (
            select(Task)
            .where(filter_expression)
            .order_by(Task.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        total = self.session.scalar(count_statement) or 0
        return list(self.session.scalars(statement)), total

    def update(self, task: Task, payload: TaskUpdate) -> Task:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
