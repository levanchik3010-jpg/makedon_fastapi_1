from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_category_service
from app.schemas.categories import (
    CategorySchema,
    CreateCategorySchema,
    UpdateCategorySchema,
)
from app.services.category import CategoryInvalidData, CategoryNotFound, CategoryService

router = APIRouter(prefix="/categories")


@router.get("", status_code=status.HTTP_200_OK)
def read_categories(
    service: CategoryService = Depends(get_category_service),
) -> list[CategorySchema]:
    return service.list_categories()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CreateCategorySchema,
    service: CategoryService = Depends(get_category_service),
) -> CategorySchema:
    try:
        return service.create_category(payload=payload)
    except CategoryInvalidData as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{category_id}")
def update_category(
    category_id: str,
    payload: UpdateCategorySchema,
    service: CategoryService = Depends(get_category_service),
) -> CategorySchema:
    try:
        return service.update_category(category_id=category_id, payload=payload)
    except CategoryNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except CategoryInvalidData as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str, service: CategoryService = Depends(get_category_service)
) -> None:
    try:
        service.delete_category(category_id=category_id)
    except CategoryNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
