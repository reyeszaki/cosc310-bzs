import json
from pathlib import Path

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "orders.json"


class OrderRepository:
    def __init__(self, data_path=DEFAULT_DATA_PATH):
        self.data_path = Path(data_path)

    def get_all(self) -> list[dict]:
        if not self.data_path.exists():
            return []
        with self.data_path.open(encoding="utf-8") as source:
            return json.load(source)

    def get_by_id(self, order_id: int) -> dict | None:
        for order in self.get_all():
            if order["id"] == order_id:
                return order
        return None

    def create(self, fields: dict) -> dict:
        orders = self.get_all()
        new_id = 1
        for order in orders:
            if order["id"] >= new_id:
                new_id = order["id"] + 1
        saved_order = fields.copy()
        saved_order["id"] = new_id
        orders.append(saved_order)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.data_path.with_suffix(".tmp")
        with temporary_path.open("w", encoding="utf-8") as target:
            json.dump(orders, target, indent=2, allow_nan=False)
        temporary_path.replace(self.data_path)
        return saved_order
