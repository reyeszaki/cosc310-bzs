from app.repository.restaurant_repo import RestaurantRepository
from app.schema.restaurant_schema import Restaurant, CreateRestaurant, UpdateRestaurant



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

    def create_restaurant(self, restaurant: CreateRestaurant) -> Restaurant:
        saved_restaurant = self.repository.create(restaurant.model_dump())
        return Restaurant(**saved_restaurant)
    def update_restaurant(self, restaurant_id: int, restaurant: UpdateRestaurant) -> Restaurant:
        saved_restaurant = self.repository.update(restaurant_id, restaurant.model_dump(),)

        if saved_restaurant is None:
            raise LookupError(f"Restaurant doesnt match with id {restaurant_id} not found")

        return Restaurant(**saved_restaurant)




