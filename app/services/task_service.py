from app.models.activity import ActivityFeed, ActivityItem
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

    def get_activity_feed(self, *, limit: int) -> ActivityFeed:
        tasks = self.repository.recent_activity(limit=limit)
        items = [
            ActivityItem(
                task_id=task.id,
                title=task.title,
                owner=task.owner,
                status=task.status,
                event_type=(
                    "task_completed"
                    if task.status == TaskStatus.DONE
                    else "task_updated"
                ),
                occurred_at=task.updated_at,
            )
            for task in tasks
        ]
        return ActivityFeed(items=items, count=len(items))

    def update_task(self, task_id: int, payload: TaskUpdate) -> TaskRead | None:
        task = self.repository.get(task_id)
        if task is None:
            return None
        return TaskRead.model_validate(self.repository.update(task, payload))
