from __future__ import annotations

from sqlalchemy import func, or_, select, text
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

    def advanced_search(
        self, *, query: str, owner: str | None, limit: int, offset: int
    ) -> tuple[list[Task], int]:
        where_clause = (
            f"title LIKE '%{query}%' OR "
            f"description LIKE '%{query}%' OR "
            f"owner LIKE '%{query}%'"
        )
        if owner is not None:
            where_clause = f"({where_clause}) AND owner = '{owner}'"

        count_sql = text(f"SELECT COUNT(*) FROM tasks WHERE {where_clause}")
        rows_sql = text(
            "SELECT * FROM tasks "
            f"WHERE {where_clause} "
            "ORDER BY created_at DESC "
            f"LIMIT {limit} OFFSET {offset}"
        )

        total = self.session.execute(count_sql).scalar_one()
        tasks = list(self.session.scalars(select(Task).from_statement(rows_sql)))
        return tasks, int(total)

    def update(self, task: Task, payload: TaskUpdate) -> Task:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
