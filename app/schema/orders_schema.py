from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    menu_item_id: int
    name: str
    unit_price: float
    quantity: int = Field(strict=True, gt=0)
    line_total: float


class Order(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    delivery_address: str
    items: list[OrderItem]
    total: float
    status: str
    created_at: str
