from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import require_subject
from app.db.session import get_session
from app.models.imports import BulkImportResult
from app.models.task import (
    PaginatedTasks,
    TaskCreate,
    TaskRead,
    TaskStatus,
    TaskUpdate,
)
from app.repositories.task_repository import TaskRepository
from app.services.task_import_service import TaskImportService
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(session: Annotated[Session, Depends(get_session)]) -> TaskService:
    return TaskService(TaskRepository(session))


def get_task_import_service(
    session: Annotated[Session, Depends(get_session)],
) -> TaskImportService:
    return TaskImportService(TaskRepository(session))


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    _: Annotated[str, Depends(require_subject)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskRead:
    return service.create_task(payload)


@router.get("", response_model=PaginatedTasks)
def list_tasks(
    _: Annotated[str, Depends(require_subject)],
    service: Annotated[TaskService, Depends(get_task_service)],
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    owner: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PaginatedTasks:
    return service.list_tasks(
        status=status_filter,
        owner=owner,
        limit=limit,
        offset=offset,
    )


@router.get("/search", response_model=PaginatedTasks)
def search_tasks(
    q: Annotated[str, Query(min_length=1, max_length=100)],
    _: Annotated[str, Depends(require_subject)],
    service: Annotated[TaskService, Depends(get_task_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PaginatedTasks:
    return service.search_tasks(query=q, limit=limit, offset=offset)


@router.post(
    "/import/csv",
    response_model=BulkImportResult,
    status_code=status.HTTP_201_CREATED,
)
def import_tasks_from_csv(
    raw_csv: Annotated[str, Body(media_type="text/csv")],
    _: Annotated[str, Depends(require_subject)],
    service: Annotated[TaskImportService, Depends(get_task_import_service)],
) -> BulkImportResult:
    return service.import_csv(raw_csv)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    _: Annotated[str, Depends(require_subject)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskRead:
    task = service.get_task(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    _: Annotated[str, Depends(require_subject)],
    service: Annotated[TaskService, Depends(get_task_service)],
) -> TaskRead:
    task = service.update_task(task_id, payload)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task
