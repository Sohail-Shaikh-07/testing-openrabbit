import csv
from io import StringIO

from app.models.imports import BulkImportResult
from app.models.task import TaskCreate, TaskPriority, TaskRead
from app.repositories.task_repository import TaskRepository


class TaskImportService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def import_csv(self, raw_csv: str) -> BulkImportResult:
        reader = csv.DictReader(StringIO(raw_csv))
        created: list[TaskRead] = []

        for row in reader:
            task = self.repository.create(
                TaskCreate(
                    title=row["title"],
                    description=row["description"],
                    owner=row["owner"],
                    priority=TaskPriority(row.get("priority", "medium")),
                )
            )
            created.append(TaskRead.model_validate(task))

        return BulkImportResult(created=len(created), items=created)
