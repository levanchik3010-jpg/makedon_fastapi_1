from pydantic import BaseModel, ConfigDict


class CategorySchema(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class CreateCategorySchema(BaseModel):
    name: str


class UpdateCategorySchema(BaseModel):
    name: str | None = None
