import json
from pathlib import Path

from app.schema.restaurant_schema import CreateRestaurant

# Points reliably to cosc310-bzs/data/restaurants.json regardless of where the terminal was launched
DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "restaurants.json"


class RestaurantRepository:
    def __init__(self, data_path: Path | str = DEFAULT_DATA_PATH) -> None:
        self.data_path = Path(data_path)

    def get_all(self) -> list[dict]:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data source not found at {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_by_id(self, restaurant_id: int) -> dict | None:
        restaurants = self.get_all()
        for item in restaurants:
            if item.get("id") == restaurant_id:
                return item
        return None


    def create(self, restaurant: dict) -> dict:
        restaurants = self.get_all()
        new_id = max(
            (item["id"] for item in restaurants),
            default=0,
        ) + 1

        saved_restaurant = {**restaurant, "id": new_id}
        restaurants.append(saved_restaurant)

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(restaurants, f, indent=2)

        return saved_restaurant

    def update(self, restaurant_id: int, restaurant: CreateRestaurant) -> dict | None:
        restaurants = self.get_all()
        for item in restaurants:
            if item.get("id") == restaurant_id:
                item.update(restaurant)
                item["id"] = restaurant_id

                with open(self.data_path, "w", encoding="utf-8") as f:
                    json.dump(restaurants, f, indent=2)
                return item
        return None

    def delete(self, restaurant_id: int) -> dict | None:
        restaurants = self.get_all()
        for item in restaurants:
            if item.get("id") == restaurant_id:
                restaurants.remove(item)
                with open(self.data_path, "w", encoding="utf-8") as f:
                    json.dump(restaurants, f, indent=2)
                return item
        return None