from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.schema.menu_schema import Menu, MenuItem, MenuItemCreate, MenuItemUpdate
from app.services.restaurant_service import RestaurantService


class MenuService:
    def __init__(self, repository: MenuRepository, restaurants: RestaurantRepository):
        self.repository = repository
        self.restaurants = restaurants
        self.restaurant_service = RestaurantService(restaurants)

    def check_restaurant(self, restaurant_id: int) -> None:
        if self.restaurants.get_by_id(restaurant_id) is None:
            raise LookupError(f"Restaurant with id {restaurant_id} not found")

    def get_menu(self, restaurant_id: int, category: str | None = None) -> Menu:
        self.check_restaurant(restaurant_id)
        raw_items = self.repository.get_by_restaurant(restaurant_id)

        if category is not None and category.strip():
            normalized = category.strip().lower()
            raw_items = [
                item for item in raw_items if item["category"].strip().lower() == normalized
            ]

        items = [MenuItem(**item) for item in raw_items]

        return Menu(restaurant_id=restaurant_id, items=items)

    def add_item(self, restaurant_id: int, item: MenuItemCreate, user=None) -> MenuItem:
        self.restaurant_service.check_management_access(restaurant_id, user)
        item_data = item.model_dump()
        item_data["restaurant_id"] = restaurant_id
        saved_item = self.repository.add(item_data)
        return MenuItem(**saved_item)

    def update_item(
        self, restaurant_id: int, item_id: int, item: MenuItemUpdate, user=None
    ) -> MenuItem:
        self.restaurant_service.check_management_access(restaurant_id, user)
        saved_item = self.repository.update(restaurant_id, item_id, item.model_dump())
        if saved_item is None:
            raise LookupError(
                f"Menu item with id {item_id} not found in restaurant {restaurant_id}"
            )
        return MenuItem(**saved_item)

    def delete_item(self, restaurant_id: int, item_id: int, user=None) -> None:
        self.restaurant_service.check_management_access(restaurant_id, user)
        deleted = self.repository.delete(restaurant_id, item_id)
        if not deleted:
            raise LookupError(
                f"Menu item with id {item_id} not found in restaurant {restaurant_id}"
            )
