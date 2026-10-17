import json
import os
import tempfile
from pathlib import Path
from threading import RLock

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "restaurants.json"


class RestaurantRepository:
    # Like menu storage, supports threads within one API worker.
    _lock = RLock()

    def __init__(self, data_path: Path | str = DEFAULT_DATA_PATH) -> None:
        self.data_path = Path(data_path)

    def get_all(self) -> list[dict]:
        with self._lock, self.data_path.open(encoding="utf-8") as source:
            return json.load(source)

    def get_by_id(self, restaurant_id: int) -> dict | None:
        return next((row for row in self.get_all() if row["id"] == restaurant_id), None)

    def _save(self, restaurants: list[dict]) -> None:
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.data_path.parent, delete=False
            ) as target:
                temporary_path = Path(target.name)
                json.dump(restaurants, target, indent=2, allow_nan=False)
                target.write("\n")
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary_path, self.data_path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    def create(self, restaurant: dict) -> dict:
        with self._lock:
            restaurants = self.get_all()
            saved = {**restaurant, "id": max((row["id"] for row in restaurants), default=0) + 1}
            restaurants.append(saved)
            self._save(restaurants)
            return saved

    def update(self, restaurant_id: int, restaurant: dict) -> dict | None:
        with self._lock:
            restaurants = self.get_all()
            for item in restaurants:
                if item["id"] == restaurant_id:
                    item.update(restaurant)
                    item["id"] = restaurant_id
                    self._save(restaurants)
                    return item
            return None

    def delete(self, restaurant_id: int) -> dict | None:
        with self._lock:
            restaurants = self.get_all()
            for item in restaurants:
                if item["id"] == restaurant_id:
                    restaurants.remove(item)
                    self._save(restaurants)
                    return item
            return None
