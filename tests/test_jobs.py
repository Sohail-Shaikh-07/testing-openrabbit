from datetime import UTC, datetime, timedelta

from app.jobs.task_summary import build_task_summary
from app.models.task import Task, TaskPriority, TaskStatus


def test_build_task_summary_counts_open_and_overdue_tasks() -> None:
    now = datetime.now(UTC)
    tasks = [
        Task(
            id=1,
            title="Overdue",
            description="Past due",
            owner="alice@example.com",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            due_at=now - timedelta(days=1),
        ),
        Task(
            id=2,
            title="Done",
            description="Already complete",
            owner="alice@example.com",
            status=TaskStatus.DONE,
            priority=TaskPriority.LOW,
            due_at=now - timedelta(days=2),
        ),
    ]

    summary = build_task_summary(tasks, now=now)

    assert summary.open_count == 1
    assert summary.overdue_count == 1
