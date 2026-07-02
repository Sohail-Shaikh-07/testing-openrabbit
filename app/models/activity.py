from datetime import datetime

from pydantic import BaseModel

from app.models.task import TaskStatus


class ActivityItem(BaseModel):
    task_id: int
    title: str
    owner: str
    status: TaskStatus
    event_type: str
    occurred_at: datetime


class ActivityFeed(BaseModel):
    items: list[ActivityItem]
    count: int
