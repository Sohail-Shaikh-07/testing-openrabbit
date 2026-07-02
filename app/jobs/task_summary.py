from datetime import UTC, datetime

from pydantic import BaseModel

from app.models.task import Task, TaskStatus


class TaskSummary(BaseModel):
    open_count: int
    overdue_count: int


def build_task_summary(tasks: list[Task], now: datetime | None = None) -> TaskSummary:
    reference_time = now or datetime.now(UTC)
    open_tasks = [task for task in tasks if task.status != TaskStatus.DONE]
    overdue_tasks = [
        task
        for task in open_tasks
        if task.due_at is not None and task.due_at < reference_time
    ]
    return TaskSummary(open_count=len(open_tasks), overdue_count=len(overdue_tasks))
