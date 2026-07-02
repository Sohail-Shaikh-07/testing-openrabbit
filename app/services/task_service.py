from app.jobs.due_date_reminders import ReminderBatch, build_overdue_reminders
from app.models.task import PaginatedTasks, TaskCreate, TaskRead, TaskStatus, TaskUpdate
from app.repositories.task_repository import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def create_task(self, payload: TaskCreate) -> TaskRead:
        return TaskRead.model_validate(self.repository.create(payload))

    def get_task(self, task_id: int) -> TaskRead | None:
        task = self.repository.get(task_id)
        if task is None:
            return None
        return TaskRead.model_validate(task)

    def list_tasks(
        self,
        *,
        status: TaskStatus | None,
        owner: str | None,
        limit: int,
        offset: int,
    ) -> PaginatedTasks:
        tasks, total = self.repository.list_tasks(
            status=status,
            owner=owner,
            limit=limit,
            offset=offset,
        )
        return PaginatedTasks(
            items=[TaskRead.model_validate(task) for task in tasks],
            total=total,
            limit=limit,
            offset=offset,
        )

    def search_tasks(self, *, query: str, limit: int, offset: int) -> PaginatedTasks:
        tasks, total = self.repository.search(query=query, limit=limit, offset=offset)
        return PaginatedTasks(
            items=[TaskRead.model_validate(task) for task in tasks],
            total=total,
            limit=limit,
            offset=offset,
        )

    def get_overdue_reminders(self) -> ReminderBatch:
        return build_overdue_reminders(self.repository.list_open())

    def update_task(self, task_id: int, payload: TaskUpdate) -> TaskRead | None:
        task = self.repository.get(task_id)
        if task is None:
            return None
        return TaskRead.model_validate(self.repository.update(task, payload))
