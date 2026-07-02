from pydantic import BaseModel

from app.models.task import TaskRead


class BulkImportResult(BaseModel):
    created: int
    items: list[TaskRead]
