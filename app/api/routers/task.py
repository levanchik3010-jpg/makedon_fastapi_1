from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Depends

from app.models.task import TaskORM
from app.schemas.tasks import TaskCreateSchema, TaskSchema, TaskUpdateSchema
from app.services.task import TaskNotFound, TaskService

router = APIRouter(prefix="/tasks")

TaskServiceDep = Annotated[TaskService, Depends()]


@router.get("")
def read_tasks(
    task_service: TaskServiceDep,
) -> list[TaskSchema]:
    return task_service.list_tasks()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema, task_service: TaskServiceDep) -> TaskSchema:

    return task_service.create_task(task_create=payload)


@router.patch("/{task_id}")
def update_task(self, task_id: str, task_update: TaskUpdateSchema) -> TaskSchema:
    task_for_update: TaskORM | None = self.task_repository.get_by_id(task_id=task_id)

    # Явная проверка на None убирает ошибку "union-attr" у Mypy
    if task_for_update is None:
        raise TaskNotFound(f"Задача с {task_id} не найдена")

    if task_update.title:
        task_for_update.title = task_update.title
    if task_update.completed is not None:
        task_for_update.completed = task_update.completed

    self.db.commit()
    return TaskSchema.model_validate(task_for_update)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(self, task_id: str) -> None:
    task_for_delete: TaskORM | None = self.task_repository.get_by_id(task_id=task_id)
    if task_for_delete is None:
        raise TaskNotFound(f"Задача с {task_id} не найдена")

    self.task_repository.delete(task_for_delete)
    self.db.commit()
