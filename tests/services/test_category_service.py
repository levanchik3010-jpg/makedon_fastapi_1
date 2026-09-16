from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.models.category import CategoryORM
from app.schemas.categories import (
    CategorySchema,
    CreateCategorySchema,
    UpdateCategorySchema,
)
from app.services.category import CategoryNotFound, CategoryService


@pytest.fixture
def mock_db() -> Session:
    """Фикстура для имитации сессии базы данных SQLAlchemy."""
    return MagicMock(spec=Session)


@pytest.fixture
def category_service(mock_db: Session) -> CategoryService:
    """Фикстура для создания инстанса CategoryService с моком репозитория."""
    service = CategoryService(mock_db)
    service.category_repository = MagicMock()
    return service


# ==========================================
# 1. Тесты для метода list_categories
# ==========================================
def test_list_categories_success(category_service: CategoryService) -> None:
    # Arrange
    mock_categories = [
        CategoryORM(id="cat-1", name="Work"),
        CategoryORM(id="cat-2", name="Personal"),
    ]
    category_service.category_repository.get_all.return_value = mock_categories

    # Act
    result = category_service.list_categories()

    # Assert
    assert len(result) == 2
    assert result == [
        CategorySchema(id="cat-1", name="Work"),
        CategorySchema(id="cat-2", name="Personal"),
    ]
    category_service.category_repository.get_all.assert_called_once()


# ==========================================
# 2. Тесты для метода create_category
# ==========================================
def test_create_category_success(
    category_service: CategoryService, mock_db: MagicMock
) -> None:
    # Arrange
    dto = CreateCategorySchema(name="Work")
    created_orm = CategoryORM(id="cat-1", name="Work")
    category_service.category_repository.create.return_value = created_orm

    # Act
    result = category_service.create_category(dto)

    # Assert
    assert result == CategorySchema(id="cat-1", name="Work")
    category_service.category_repository.create.assert_called_once_with(name="Work")
    mock_db.commit.assert_called_once()


# ==========================================
# 3. Тесты для метода update_category
# ==========================================
def test_update_category_success(
    category_service: CategoryService, mock_db: MagicMock
) -> None:
    # Arrange
    cat_id = "cat-1"
    dto = UpdateCategorySchema(name="Work Updated")
    existing_orm = CategoryORM(id=cat_id, name="Work")

    category_service.category_repository.get_by_id.return_value = existing_orm

    # Act
    result = category_service.update_category(cat_id, dto)

    # Assert
    assert result.name == "Work Updated"
    assert existing_orm.name == "Work Updated"
    category_service.category_repository.get_by_id.assert_called_once_with(cat_id)
    mock_db.commit.assert_called_once()


def test_update_category_not_found(category_service: CategoryService) -> None:
    # Arrange
    cat_id = "non-existing"
    dto = UpdateCategorySchema(name="Work Updated")
    category_service.category_repository.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(CategoryNotFound):
        category_service.update_category(cat_id, dto)

    category_service.category_repository.get_by_id.assert_called_once_with(cat_id)


# ==========================================
# 4. Тесты для метода delete_category
# ==========================================
def test_delete_category_success(
    category_service: CategoryService, mock_db: MagicMock
) -> None:
    # Arrange
    cat_id = "cat-1"
    existing_orm = CategoryORM(id=cat_id, name="Work")
    category_service.category_repository.get_by_id.return_value = existing_orm

    # Act
    category_service.delete_category(cat_id)

    # Assert
    category_service.category_repository.get_by_id.assert_called_once_with(cat_id)
    category_service.category_repository.delete.assert_called_once_with(existing_orm)
    mock_db.commit.assert_called_once()


def test_delete_category_not_found(category_service: CategoryService) -> None:
    # Arrange
    cat_id = "non-existing"
    category_service.category_repository.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(CategoryNotFound):
        category_service.delete_category(cat_id)

    category_service.category_repository.get_by_id.assert_called_once_with(cat_id)
    category_service.category_repository.delete.assert_not_called()
