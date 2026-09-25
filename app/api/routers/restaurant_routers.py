from fastapi import APIRouter, HTTPException, status

from app.repository.restaurant_repo import RestaurantRepository
from app.schema.restaurant_schema import Restaurant
from app.services.restaurant_service import RestaurantService

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

repo = RestaurantRepository()
service = RestaurantService(repo)


@router.get("", response_model=list[Restaurant])
def get_restaurants() -> list[Restaurant]:
    return service.list_restaurants()


@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: int) -> Restaurant:
    try:
        return service.get_restaurant(restaurant_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )