from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    id: int
    name: str = Field(min_length=1)
    cuisine: str
    address: str
    is_open: bool

class CreateRestaurant(BaseModel):
    name: str = Field(min_length=1)
    cuisine: str = Field(min_length=1)
    address: str = Field(min_length=1)
    is_open: bool

class UpdateRestaurant(BaseModel):
    name: str = Field(min_length=1)
    cuisine: str = Field(min_length=1)
    address: str = Field(min_length=1)
    is_open: bool
