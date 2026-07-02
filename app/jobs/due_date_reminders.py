from datetime import UTC, datetime
from typing import cast

from pydantic import BaseModel

from app.models.task import Task, TaskStatus


class TaskReminder(BaseModel):
    task_id: int
    title: str
    owner: str
    due_at: datetime
    message: str


class ReminderBatch(BaseModel):
    items: list[TaskReminder]
    count: int


def build_overdue_reminders(
    tasks: list[Task], now: datetime | None = None
) -> ReminderBatch:
    reference_date = (now or datetime.now(UTC)).date()
    reminders: list[TaskReminder] = []

    for task in tasks:
        if task.status == TaskStatus.DONE:
            continue
        due_at = cast(datetime, task.due_at)
        if due_at.date() <= reference_date:
            reminders.append(
                TaskReminder(
                    task_id=task.id,
                    title=task.title,
                    owner=task.owner,
                    due_at=due_at,
                    message=f"{task.title} is overdue",
                )
            )

    return ReminderBatch(items=reminders, count=len(reminders))
