from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class CreateRestaurant(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Text
    cuisine: Text
    address: Text
    is_open: bool


class Restaurant(CreateRestaurant):
    id: int = Field(gt=0)


class UpdateRestaurant(CreateRestaurant):
    """PUT requires all editable fields, just like creation."""
