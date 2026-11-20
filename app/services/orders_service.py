from datetime import datetime, timezone

from app.schema.orders_schema import Order


class OrderService:
    def __init__(self, repository):
        self.repository = repository

    def create_order(self, customer_id: int, restaurant_id: int, address: str,
                     items: list[dict], total: float) -> Order:
        fields = {
            "customer_id": customer_id,
            "restaurant_id": restaurant_id,
            "delivery_address": address,
            "items": items,
            "total": total,
            "status": "Placed",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return Order(**self.repository.create(fields))

    def get_order(self, customer_id: int, order_id: int) -> Order:
        order = self.repository.get_by_id(order_id)
        if order is None or order["customer_id"] != customer_id:
            raise LookupError("Order not found")
        return Order(**order)

    def get_orders(self, customer_id: int) -> list[Order]:
        orders = []
        for order in self.repository.get_all():
            if order["customer_id"] == customer_id:
                orders.append(Order(**order))
        return orders
