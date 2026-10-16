import json
import os
import tempfile
from pathlib import Path
from threading import RLock

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "menu_items.json"


class MenuRepository:
    # Serializes read-modify-write operations across instances in this API process.
    # RLock allows a mutation holding the lock to call get_all(), which also locks.
    _lock = RLock()

    def __init__(self, data_path: Path | str = DEFAULT_DATA_PATH) -> None:
        self.data_path = Path(data_path)

    def get_all(self) -> list[dict]:
        with self._lock:
            # A restaurant may have no items yet; first add creates the menu file.
            if not self.data_path.exists():
                return []
            with self.data_path.open(encoding="utf-8") as source:
                return json.load(source)

    def get_by_restaurant(self, restaurant_id: int) -> list[dict]:
        return [item for item in self.get_all() if item["restaurant_id"] == restaurant_id]

    def _save(self, items: list[dict]) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            # Write beside the data file so replace is atomic on the same filesystem.
            # The old file stays intact if writing or replacing the new file fails.
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.data_path.parent, delete=False
            ) as target:
                temporary_path = Path(target.name)
                json.dump(items, target, indent=2, allow_nan=False)
                target.write("\n")
                target.flush()
                os.fsync(target.fileno())
            os.replace(temporary_path, self.data_path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    def add(self, fields: dict) -> dict:
        with self._lock:
            items = self.get_all()
            item = {**fields, "id": max((row["id"] for row in items), default=0) + 1}
            items.append(item)
            self._save(items)
            return item

    def update(self, restaurant_id: int, item_id: int, fields: dict) -> dict | None:
        with self._lock:
            items = self.get_all()
            for item in items:
                # Both IDs must match to prevent changing another restaurant's item.
                if item["restaurant_id"] == restaurant_id and item["id"] == item_id:
                    item.update(fields)
                    self._save(items)
                    return item
            return None

    def delete(self, restaurant_id: int, item_id: int) -> bool:
        with self._lock:
            items = self.get_all()
            remaining = [item for item in items if not (
                item["restaurant_id"] == restaurant_id and item["id"] == item_id
            )]
            if len(remaining) == len(items):
                return False
            self._save(remaining)
            return True
