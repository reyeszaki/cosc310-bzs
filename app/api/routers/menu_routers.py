from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.schema.menu_schema import Menu, MenuError, MenuItem, MenuItemCreate, MenuItemUpdate
from app.services.menu_service import MenuService

router = APIRouter(prefix="/restaurants/{restaurant_id}/menu", tags=["menus"])
repo = MenuRepository()
service = MenuService(repo, RestaurantRepository())

RestaurantID = Annotated[int, Path(gt=0, description="Existing restaurant ID")]
ItemID = Annotated[int, Path(gt=0, description="Menu item ID belonging to this restaurant")]


def get_menu_service() -> MenuService:
    # Dependency overrides let tests use temporary files instead of real menu data.
    return service


Service = Annotated[MenuService, Depends(get_menu_service)]
NOT_FOUND = {
    404: {
        "model": MenuError,
        "description": "Restaurant does not exist, or item does not belong to this restaurant",
    }
}


@router.get(
    "",
    response_model=Menu,
    responses=NOT_FOUND,
    summary="View a restaurant's menu",
    description=(
        "Return names, descriptions, prices, categories, and availability. "
        "Unavailable items remain visible. An unknown category or empty menu returns an empty list."
    ),
)
def get_menu(
    restaurant_id: RestaurantID,
    menu_service: Service,
    category: str | None = Query(
        default=None,
        description="Filter by category, ignoring case and surrounding spaces. Omit or leave blank to show all items.",
    ),
) -> Menu:
    try:
        return menu_service.get_menu(restaurant_id, category)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/items",
    response_model=MenuItem,
    status_code=status.HTTP_201_CREATED,
    responses=NOT_FOUND,
    summary="Add a menu item",
    description=(
        "Requires name, description, positive price, and category. Availability defaults to true. "
        "IDs are assigned by the server. Invalid input returns 422; successful changes are saved to JSON."
    ),
)
def add_item(
    restaurant_id: RestaurantID, request: MenuItemCreate, menu_service: Service
) -> MenuItem:
    try:
        return menu_service.add_item(restaurant_id, request)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch(
    "/items/{item_id}",
    response_model=MenuItem,
    responses=NOT_FOUND,
    summary="Update a menu item",
    description=(
        "Change one or more editable fields, including availability. Omitted fields remain unchanged. "
        "Empty requests, null values, unknown fields, and invalid prices return 422. "
        "The updated item is saved to JSON and visible on the next menu request."
    ),
)
def update_item(
    restaurant_id: RestaurantID, item_id: ItemID,
    request: MenuItemUpdate, menu_service: Service,
) -> MenuItem:
    try:
        return menu_service.update_item(restaurant_id, item_id, request)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=NOT_FOUND,
    summary="Remove a menu item",
    description="Permanently remove this restaurant's item from JSON. Returns no response body on success.",
)
def delete_item(
    restaurant_id: RestaurantID, item_id: ItemID, menu_service: Service
) -> Response:
    try:
        menu_service.delete_item(restaurant_id, item_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
