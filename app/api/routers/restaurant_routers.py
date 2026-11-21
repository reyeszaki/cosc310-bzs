from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import require_role, user_service
from app.schema.users_schema import UserPublic
from app.schema.restaurant_schema import AssignRestaurantOwner

from app.repository.restaurant_repo import RestaurantRepository
from app.schema.restaurant_schema import Restaurant, CreateRestaurant, UpdateRestaurant
from app.services.restaurant_service import RestaurantService

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

repo = RestaurantRepository()
service = RestaurantService(repo)


@router.get("", response_model=list[Restaurant], response_model_exclude_none=True)
def get_restaurants(
    search: str | None = None,
    cuisine: str | None = None,
    is_open: bool | None = None,
) -> list[Restaurant]:
    return service.search_restaurants(search=search, cuisine=cuisine, is_open=is_open)


@router.get("/{restaurant_id}", response_model=Restaurant, response_model_exclude_none=True)
def get_restaurant(restaurant_id: int) -> Restaurant:
    try:
        return service.get_restaurant(restaurant_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

@router.post("", response_model=Restaurant, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED, responses={401: {"description": "Sign-in required"},
    403: {"description": "Management access denied"},
    404: {"description": "Restaurant or owner not found"}})
def create_restaurant(restaurant: CreateRestaurant,
                      user: UserPublic = Depends(require_role("owner", "admin"))) -> Restaurant:
    return service.create_restaurant(restaurant, user)

@router.put("/{restaurant_id}", response_model=Restaurant, response_model_exclude_none=True, responses={401: {"description": "Sign-in required"},
    403: {"description": "Management access denied"},
    404: {"description": "Restaurant or owner not found"}})
def update_restaurant(
    restaurant_id: int,
    restaurant: UpdateRestaurant,
    user: UserPublic = Depends(require_role("owner", "admin")),) -> Restaurant:
    try:
        return service.update_restaurant(restaurant_id, restaurant, user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
@router.delete("/{restaurant_id}", response_model=Restaurant, response_model_exclude_none=True, responses={401: {"description": "Sign-in required"},
    403: {"description": "Management access denied"},
    404: {"description": "Restaurant or owner not found"}})
def delete_restaurant(restaurant_id: int,
                      user: UserPublic = Depends(require_role("owner", "admin"))) -> Restaurant:
    try:
        return service.delete_restaurant(restaurant_id, user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc),)


@router.put("/{restaurant_id}/owner", response_model=Restaurant, response_model_exclude_none=True,
            summary="Assign or remove a restaurant owner (admin only)", responses={401: {"description": "Sign-in required"},
    403: {"description": "Management access denied"},
    404: {"description": "Restaurant or owner not found"}})
def assign_owner(restaurant_id: int, request: AssignRestaurantOwner,
                 user: UserPublic = Depends(require_role("admin"))) -> Restaurant:
    try:
        return service.assign_owner(restaurant_id, request.owner_id, user, user_service)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
