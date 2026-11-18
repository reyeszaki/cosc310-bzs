import json
from pathlib import Path

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "menu_categories.json"


class CategoryRepository:
    def __init__(self, data_path: Path | str = DEFAULT_DATA_PATH) -> None:
        self.data_path = Path(data_path)

    def get_all(self) -> list[dict]:
        if not self.data_path.exists():
            return []
        with self.data_path.open(encoding="utf-8") as source:
            return json.load(source)

    def get_by_restaurant(self, restaurant_id: int) -> list[str]:
        names = []
        for category in self.get_all():
            if category["restaurant_id"] == restaurant_id:
                names.append(category["name"])
        return names

    def save_for_restaurant(self, restaurant_id: int, names: list[str]) -> None:
        categories = []
        for category in self.get_all():
            if category["restaurant_id"] != restaurant_id:
                categories.append(category)
        for name in names:
            categories.append({"restaurant_id": restaurant_id, "name": name})
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        with self.data_path.open("w", encoding="utf-8") as target:
            json.dump(categories, target, indent=2)
