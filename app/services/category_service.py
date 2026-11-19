from app.repository.category_repo import CategoryRepository
from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository


class CategoryService:
    def __init__(self, categories: CategoryRepository, menus: MenuRepository,
                 restaurants: RestaurantRepository) -> None:
        self.categories = categories
        self.menus = menus
        self.restaurants = restaurants

    def get_categories(self, restaurant_id: int) -> list[str]:
        if self.restaurants.get_by_id(restaurant_id) is None:
            raise LookupError(f"Restaurant with id {restaurant_id} not found")
        names = self.categories.get_by_restaurant(restaurant_id)
        # Existing menus keep working without a data migration.
        for item in self.menus.get_by_restaurant(restaurant_id):
            exists = False
            for name in names:
                if name.casefold() == item["category"].casefold():
                    exists = True
                    break
            if not exists:
                names.append(item["category"])
        return names

    def create_category(self, restaurant_id: int, name: str) -> list[str]:
        names = self.get_categories(restaurant_id)
        for current in names:
            if current.casefold() == name.casefold():
                raise ValueError("Category already exists")
        names.append(name)
        self.categories.save_for_restaurant(restaurant_id, names)
        return names

    def rename_category(self, restaurant_id: int, name: str, new_name: str) -> list[str]:
        names = self.get_categories(restaurant_id)
        if name.casefold() not in [current.casefold() for current in names]:
            raise LookupError("Category not found")
        for current in names:
            if current.casefold() == new_name.casefold() and current.casefold() != name.casefold():
                raise ValueError("Category already exists")
        renamed = []
        for current in names:
            if current.casefold() == name.casefold():
                renamed.append(new_name)
            else:
                renamed.append(current)
        items = self.menus.get_all()
        for item in items:
            if item["restaurant_id"] == restaurant_id and item["category"].casefold() == name.casefold():
                item["category"] = new_name
        self.menus.save(items)
        self.categories.save_for_restaurant(restaurant_id, renamed)
        return renamed

    def delete_category(self, restaurant_id: int, name: str) -> None:
        names = self.get_categories(restaurant_id)
        if name.casefold() not in [current.casefold() for current in names]:
            raise LookupError("Category not found")
        for item in self.menus.get_by_restaurant(restaurant_id):
            if item["category"].casefold() == name.casefold():
                raise ValueError("Move or delete the items in this category first")
        remaining = []
        for current in names:
            if current.casefold() != name.casefold():
                remaining.append(current)
        self.categories.save_for_restaurant(restaurant_id, remaining)
