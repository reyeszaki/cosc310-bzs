from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from app.repository.restaurant_repo import RestaurantRepository
from app.schema.restaurant_schema import Restaurant, CreateRestaurant, UpdateRestaurant
from app.services.restaurant_service import RestaurantService

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

repo = RestaurantRepository()
service = RestaurantService(repo)

NOT_FOUND = {404: {"description": "Restaurant does not exist; response contains detail"}}

RestaurantID = Annotated[int, Path(gt=0, description="Existing restaurant ID")]


@router.get("", response_model=list[Restaurant])
def get_restaurants(
    search: str | None = None,
    cuisine: str | None = None,
    is_open: bool | None = None,
) -> list[Restaurant]:
    """Search name substrings and filter exact cuisine/open status; filters combine with AND.

    Text matching ignores case and surrounding spaces; blank text means no filter.
    """
    return service.search_restaurants(search=search, cuisine=cuisine, is_open=is_open)


@router.get("/{restaurant_id}", response_model=Restaurant, responses=NOT_FOUND)
def get_restaurant(restaurant_id: RestaurantID) -> Restaurant:
    try:
        return service.get_restaurant(restaurant_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

@router.post("", response_model=Restaurant, status_code=status.HTTP_201_CREATED)
def create_restaurant(restaurant: CreateRestaurant) -> Restaurant:
    """Persist a restaurant with a generated ID. All four editable fields are required."""
    return service.create_restaurant(restaurant)

@router.put("/{restaurant_id}", response_model=Restaurant, responses=NOT_FOUND)
def update_restaurant(
    restaurant_id: RestaurantID,
    restaurant: UpdateRestaurant,) -> Restaurant:
    """Replace all editable fields; the restaurant ID stays unchanged."""
    try:
        return service.update_restaurant(restaurant_id, restaurant)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
@router.delete("/{restaurant_id}", response_model=Restaurant, responses={**NOT_FOUND, 409: {"description": "Remove menu items before deleting the restaurant"}})
def delete_restaurant(restaurant_id: RestaurantID) -> Restaurant:
    try:
        return service.delete_restaurant(restaurant_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc),)



