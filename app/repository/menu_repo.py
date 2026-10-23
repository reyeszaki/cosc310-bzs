import json
from pathlib import Path

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "menu_items.json"


class MenuRepository:
    def __init__(self, data_path: Path | str = DEFAULT_DATA_PATH) -> None:
        self.data_path = Path(data_path)

    def get_all(self) -> list[dict]:
        # A restaurant can have an empty menu before the first item is added.
        if not self.data_path.exists():
            return []
        with self.data_path.open(encoding="utf-8") as source:
            return json.load(source)

    def get_by_restaurant(self, restaurant_id: int) -> list[dict]:
        items = self.get_all()
        restaurant_items = []
        for item in items:
            if item["restaurant_id"] == restaurant_id:
                restaurant_items.append(item)
        return restaurant_items

    def save(self, items: list[dict]) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with self.data_path.open("w", encoding="utf-8") as target:
            json.dump(items, target, indent=2, allow_nan=False)

    def add(self, item_data: dict) -> dict:
        items = self.get_all()
        new_id = 1
        for item in items:
            if item["id"] >= new_id:
                new_id = item["id"] + 1

        saved_item = item_data.copy()
        saved_item["id"] = new_id
        items.append(saved_item)
        self.save(items)
        return saved_item

    def update(self, restaurant_id: int, item_id: int, item_data: dict) -> dict | None:
        items = self.get_all()
        for item in items:
            # Match both IDs so another restaurant's item cannot be changed.
            if item["restaurant_id"] == restaurant_id and item["id"] == item_id:
                item.update(item_data)
                self.save(items)
                return item
        return None

    def delete(self, restaurant_id: int, item_id: int) -> bool:
        items = self.get_all()
        for item in items:
            if item["restaurant_id"] == restaurant_id and item["id"] == item_id:
                items.remove(item)
                self.save(items)
                return True
        return False
