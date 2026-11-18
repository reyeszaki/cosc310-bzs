from pydantic import BaseModel, ConfigDict, Field


class CategoryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=80)


class CategoryRename(CategoryRequest):
    new_name: str = Field(min_length=1, max_length=80)
