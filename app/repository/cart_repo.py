

# loading and saving the cart in carts.json

import json
from pathlib import Path
from threading import Lock


class CartRepository:
    def __init__(self, file_path: str | Path = "data/carts.json") -> None:
        self.file_path = Path(file_path)
        self._lock = Lock()

    def _load(self) -> dict:
        if not self.file_path.exists():
            return {}

        with self.file_path.open(encoding="utf-8") as file:
            return json.load(file)

    def get_by_customer(self, customer_id: int) -> dict | None:
        with self._lock:
            carts = self._load()
            return carts.get(str(customer_id))

    def save(self, cart: dict) -> None:
        with self._lock:
            carts = self._load()
            carts[str(cart["customer_id"])] = cart

            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.file_path.with_suffix(".tmp")

            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(carts, file, indent=2)

            temp_path.replace(self.file_path)