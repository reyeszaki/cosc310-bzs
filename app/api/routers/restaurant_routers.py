from fastapi import APIRouter, HTTPException, status
from app.models.restaurant import Restaurant
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.restaurant_service import RestaurantService

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

# Instantiate dependencies (using default data path)
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