from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.schema.menu_schema import Menu, MenuItem, MenuItemCreate, MenuItemUpdate


class MenuService:
    def __init__(self, repository: MenuRepository, restaurants: RestaurantRepository) -> None:
        self.repository = repository
        self.restaurants = restaurants

    def _require_restaurant(self, restaurant_id: int) -> None:
        if self.restaurants.get_by_id(restaurant_id) is None:
            raise LookupError(f"Restaurant with id {restaurant_id} not found")

    def get_menu(self, restaurant_id: int, category: str | None = None) -> Menu:
        self._require_restaurant(restaurant_id)
        items = [MenuItem(**row) for row in self.repository.get_by_restaurant(restaurant_id)]
        # An absent or blank filter means the full menu. Matching ignores case.
        if category and category.strip():
            selected_category = category.strip().casefold()
            items = [item for item in items if item.category.casefold() == selected_category]
        return Menu(restaurant_id=restaurant_id, items=items)

    def add_item(self, restaurant_id: int, request: MenuItemCreate) -> MenuItem:
        self._require_restaurant(restaurant_id)
        fields = request.model_dump(mode="json")
        fields["restaurant_id"] = restaurant_id
        return MenuItem(**self.repository.add(fields))

    def update_item(self, restaurant_id: int, item_id: int, request: MenuItemUpdate) -> MenuItem:
        self._require_restaurant(restaurant_id)
        # Only supplied fields are changed; omitted fields keep their stored values.
        fields = request.model_dump(exclude_unset=True)
        # JSON cannot store Decimal directly. Validation has already checked precision.
        if "price" in fields:
            fields["price"] = float(fields["price"])
        result = self.repository.update(restaurant_id, item_id, fields)
        if result is not None:
            return MenuItem(**result)
        raise LookupError(f"Menu item with id {item_id} not found in restaurant {restaurant_id}")

    def delete_item(self, restaurant_id: int, item_id: int) -> None:
        self._require_restaurant(restaurant_id)
        if not self.repository.delete(restaurant_id, item_id):
            raise LookupError(f"Menu item with id {item_id} not found in restaurant {restaurant_id}")
