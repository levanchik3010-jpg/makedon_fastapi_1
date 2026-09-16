from unittest.mock import Mock

import pytest

from app.models.task import TaskORM
from app.schemas.tasks import TaskCreateSchema, TaskSchema, TaskUpdateSchema
from app.services.task import TaskNotFoundError, TaskService


@pytest.fixture
def db_mock() -> Mock:
    return Mock()


@pytest.fixture
def repository_mock() -> Mock:
    return Mock()


@pytest.fixture
def service(db_mock: Mock, repository_mock: Mock) -> TaskService:
    service_instance = TaskService(db=db_mock)
    service_instance.task_repository = repository_mock
    return service_instance


def test_list_tasks_returns_pydantic_models(
    service: TaskService,
    repository_mock: Mock,
) -> None:
    repository_mock.get_all.return_value = [
        TaskORM(id="task-1", title="Изучить pytest", completed=False),
        TaskORM(id="task-2", title="Написать первый тест", completed=True),
    ]

    result = service.list_tasks()

    assert result == [
        TaskSchema(id="task-1", title="Изучить pytest", completed=False),
        TaskSchema(id="task-2", title="Написать первый тест", completed=True),
    ]


def test_create_task_commits_created_task(
    service: TaskService,
    db_mock: Mock,
    repository_mock: Mock,
) -> None:
    created_task = TaskORM(id="task-1", title="Новая задача", completed=False)
    repository_mock.create.return_value = created_task

    result = service.create_task(TaskCreateSchema(title="Новая задача"))

    repository_mock.create.assert_called_once_with(title="Новая задача")
    db_mock.commit.assert_called_once_with()
    assert result.model_dump() == {
        "id": "task-1",
        "title": "Новая задача",
        "completed": False,
    }


@pytest.mark.parametrize(
    ("payload", "expected_title", "expected_completed"),
    [
        pytest.param(
            TaskUpdateSchema(title="Обновить заголовок"),
            "Обновить заголовок",
            False,
        ),
        pytest.param(
            TaskUpdateSchema(completed=True),
            "Старая задача",
            True,
        ),
        pytest.param(
            TaskUpdateSchema(title="Готово", completed=True),
            "Готово",
            True,
        ),
    ],
)
def test_update_task_updates_only_passed_fields(
    service: TaskService,
    db_mock: Mock,
    repository_mock: Mock,
    payload: TaskUpdateSchema,
    expected_title: str,
    expected_completed: bool,
) -> None:
    task = TaskORM(id="task-1", title="Старая задача", completed=False)
    repository_mock.get_by_id.return_value = task

    result = service.update_task("task-1", payload)

    repository_mock.get_by_id.assert_called_once_with(task_id="task-1")
    db_mock.commit.assert_called_once_with()
    assert result.model_dump() == {
        "id": "task-1",
        "title": expected_title,
        "completed": expected_completed,
    }


def test_update_task_raises_when_task_not_found(
    service: TaskService,
    db_mock: Mock,
    repository_mock: Mock,
) -> None:
    repository_mock.get_by_id.return_value = None

    with pytest.raises(TaskNotFoundError):
        service.update_task("missing-task", TaskUpdateSchema(title="Неважно"))

    db_mock.commit.assert_not_called()
