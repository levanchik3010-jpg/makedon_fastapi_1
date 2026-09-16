from sqlalchemy.orm import Session

from app.repositories.category import CategoryRepository
from app.schemas.categories import (
    CategorySchema,
    CreateCategorySchema,
    UpdateCategorySchema,
)


class CategoryNotFound(Exception):
    """Категория не найдена"""


class CategoryInvalidData(Exception):
    """Некорректные данные категории"""


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.category_repository = CategoryRepository(db)

    def list_categories(self) -> list[CategorySchema]:
        categories_orm = self.category_repository.get_all()
        return [CategorySchema.model_validate(cat) for cat in categories_orm]

    def create_category(self, payload: CreateCategorySchema) -> CategorySchema:
        if not payload.name.strip():
            raise CategoryInvalidData("Название категории не может быть пустым")

        category_orm = self.category_repository.create(name=payload.name)
        self.db.commit()
        return CategorySchema.model_validate(category_orm)

    def update_category(
        self, category_id: str, payload: UpdateCategorySchema
    ) -> CategorySchema:
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise CategoryNotFound(f"Категория с id {category_id} не найдена")

        if payload.name is not None:
            if not payload.name.strip():
                raise CategoryInvalidData("Название категории не может быть пустым")
            category.name = payload.name

        self.db.commit()
        self.db.refresh(category)
        return CategorySchema.model_validate(category)

    def delete_category(self, category_id: str) -> None:
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise CategoryNotFound(f"Категория с id {category_id} не найдена")

        self.category_repository.delete(category)
        self.db.commit()
