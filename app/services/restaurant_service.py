from app.models.restaurant import Restaurant
from app.repositories.restaurant_repository import RestaurantRepository


class RestaurantService:
    def __init__(self, repository: RestaurantRepository) -> None:
        self.repository = repository

    def list_restaurants(self) -> list[Restaurant]:
        raw_items = self.repository.get_all()
        return [Restaurant(**item) for item in raw_items]

    def get_restaurant(self, restaurant_id: int) -> Restaurant:
        raw_item = self.repository.get_by_id(restaurant_id)
        if raw_item is None:
            raise LookupError(f"Restaurant with id {restaurant_id} not found")
        return Restaurant(**raw_item)