from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


PositiveID = Annotated[int, Field(strict=True, gt=0)]
Quantity = Annotated[int, Field(strict=True, gt=0)]


class CartItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    restaurant_id: PositiveID
    menu_item_id: PositiveID
    quantity: Quantity = 1


class CartItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: Quantity


class CartItem(BaseModel):
    menu_item_id: PositiveID
    name: str
    unit_price: Decimal
    quantity: Quantity
    line_total: Decimal


class Cart(BaseModel):
    customer_id: PositiveID
    restaurant_id: PositiveID | None
    items: list[CartItem]
    subtotal: Decimal
    total: Decimal