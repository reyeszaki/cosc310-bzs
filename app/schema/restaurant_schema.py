from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    id: int
    name: str = Field(min_length=1)
    cuisine: str
    address: str
    is_open: bool = True