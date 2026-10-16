from fastapi import APIRouter, HTTPException, status

from app.repository.restaurant_repo import RestaurantRepository
from app.schema.restaurant_schema import Restaurant, CreateRestaurant, UpdateRestaurant
from app.services.restaurant_service import RestaurantService

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

repo = RestaurantRepository()
service = RestaurantService(repo)


@router.get("", response_model=list[Restaurant])
def get_restaurants(
    search: str | None = None,
    cuisine: str | None = None,
    is_open: bool | None = None,
) -> list[Restaurant]:
    return service.search_restaurants(search=search, cuisine=cuisine, is_open=is_open)


@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: int) -> Restaurant:
    try:
        return service.get_restaurant(restaurant_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

@router.post("", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
def create_restaurant(restaurant: CreateRestaurant) -> Restaurant:
    return service.create_restaurant(restaurant)

@router.put("/{restaurant_id}", response_model=Restaurant)
def update_restaurant(
    restaurant_id: int,
    restaurant: UpdateRestaurant,) -> Restaurant:
    try:
        return service.update_restaurant(restaurant_id, restaurant)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


