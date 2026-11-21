from app.repository.restaurant_repo import RestaurantRepository
from app.schema.restaurant_schema import CreateRestaurant, Restaurant, UpdateRestaurant


class RestaurantService:
    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def get_restaurant(self, restaurant_id: int) -> Restaurant:
        raw_item = self.repository.get_by_id(restaurant_id)
        if raw_item is None:
            raise LookupError(f"Restaurant with id {restaurant_id} not found")
        return Restaurant(**raw_item)

    def require_manager(self, user) -> None:
        if user is None or not user.is_active or user.role not in ("owner", "admin"):
            raise PermissionError("Restaurant management access required")

    def check_management_access(self, restaurant_id: int, user) -> None:
        self.require_manager(user)
        restaurant = self.get_restaurant(restaurant_id)
        if user.role != "admin" and restaurant.owner_id != user.id:
            raise PermissionError("You can only manage your own restaurant")

    def create_restaurant(self, restaurant: CreateRestaurant, user=None) -> Restaurant:
        self.require_manager(user)
        fields = restaurant.model_dump()
        if user.role == "owner":
            fields["owner_id"] = user.id
        saved_restaurant = self.repository.create(fields)
        return Restaurant(**saved_restaurant)

    def update_restaurant(
        self, restaurant_id: int, restaurant: UpdateRestaurant, user=None
    ) -> Restaurant:
        self.check_management_access(restaurant_id, user)
        saved_restaurant = self.repository.update(
            restaurant_id,
            restaurant.model_dump(),
        )

        if saved_restaurant is None:
            raise LookupError(f"Restaurant with id {restaurant_id} not found")

        return Restaurant(**saved_restaurant)

    def delete_restaurant(self, restaurant_id: int, user=None) -> Restaurant:
        self.check_management_access(restaurant_id, user)
        deleted = self.repository.delete(restaurant_id)

        if deleted is None:
            raise LookupError(f"Restaurant with id {restaurant_id} not found")
        return Restaurant(**deleted)

    def assign_owner(
        self, restaurant_id: int, owner_id: int | None, user, users
    ) -> Restaurant:
        self.require_manager(user)
        if user.role != "admin":
            raise PermissionError("Only admins can assign restaurant owners")
        self.get_restaurant(restaurant_id)
        if owner_id is not None:
            owner = users.require_active(owner_id)
            if owner.role != "owner":
                raise ValueError("Choose an active owner account")
        saved = self.repository.update(restaurant_id, {"owner_id": owner_id})
        return Restaurant(**saved)

    def search_restaurants(
        self,
        search: str | None = None,
        cuisine: str | None = None,
        is_open: bool | None = None,
    ) -> list[Restaurant]:
        restaurants = [Restaurant(**r) for r in self.repository.get_all()]

        if search:
            q = search.strip().lower()
            if q:
                restaurants = [r for r in restaurants if q in r.name.lower()]

        if cuisine:
            c = cuisine.strip().lower()
            if c:
                restaurants = [r for r in restaurants if r.cuisine.strip().lower() == c]

        if is_open is not None:
            restaurants = [r for r in restaurants if r.is_open == is_open]

        return restaurants