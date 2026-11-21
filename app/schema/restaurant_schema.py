from pydantic import BaseModel, ConfigDict, Field


class Restaurant(BaseModel):
    id: int
    name: str = Field(min_length=1)
    cuisine: str
    address: str
    is_open: bool
    owner_id: int | None = Field(default=None, gt=0)

class CreateRestaurant(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    cuisine: str = Field(min_length=1)
    address: str = Field(min_length=1)
    is_open: bool

class UpdateRestaurant(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    cuisine: str = Field(min_length=1)
    address: str = Field(min_length=1)
    is_open: bool


class AssignRestaurantOwner(BaseModel):
    model_config = ConfigDict(extra="forbid")
    owner_id: int | None = Field(default=None, gt=0)
    

