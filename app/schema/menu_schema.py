from pydantic import BaseModel, ConfigDict, Field


class MenuItemCreate(BaseModel):
    # Reject unknown fields and remove spaces around text.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    price: float = Field(gt=0, le=99999999.99, multiple_of=0.01, allow_inf_nan=False)
    category: str = Field(min_length=1)
    is_available: bool = True


class MenuItemUpdate(MenuItemCreate):
    # PUT sends all editable fields, including availability.
    is_available: bool


class MenuItem(MenuItemCreate):
    id: int = Field(gt=0)
    restaurant_id: int = Field(gt=0)


class Menu(BaseModel):
    restaurant_id: int
    items: list[MenuItem]
