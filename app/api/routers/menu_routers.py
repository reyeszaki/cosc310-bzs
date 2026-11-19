from fastapi import APIRouter, HTTPException, Path, Response, status

from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.schema.menu_schema import Menu, MenuItem, MenuItemCreate, MenuItemUpdate
from app.services.menu_service import MenuService

router = APIRouter(prefix="/restaurants/{restaurant_id}/menu", tags=["menus"])
repo = MenuRepository()
service = MenuService(repo, RestaurantRepository())


@router.get(
    "", response_model=Menu,
    summary="View a restaurant's menu",
    description="Return menu items with descriptions, prices and availability. Filter by category, or leave it blank to show all items.",
    responses={404: {"description": "Restaurant not found"}},
)
def get_menu(restaurant_id: int = Path(gt=0), category: str | None = None) -> Menu:
    try:
        return service.get_menu(restaurant_id, category)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post(
    "/items", response_model=MenuItem, status_code=status.HTTP_201_CREATED,
    summary="Add a menu item",
    description="Add an item to an existing restaurant and save it to JSON. The server assigns the item ID.",
    responses={404: {"description": "Restaurant not found"}},
)
def add_item(item: MenuItemCreate, restaurant_id: int = Path(gt=0)) -> MenuItem:
    try:
        return service.add_item(restaurant_id, item)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put(
    "/items/{item_id}", response_model=MenuItem,
    summary="Update a menu item",
    description="Replace all editable fields of an item belonging to this restaurant. Send name, description, price, category and is_available.",
    responses={404: {"description": "Restaurant or menu item not found"}},
)
def update_item(item: MenuItemUpdate, restaurant_id: int = Path(gt=0),
                item_id: int = Path(gt=0)) -> MenuItem:
    try:
        return service.update_item(restaurant_id, item_id, item)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete(
    "/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a menu item",
    description="Delete an item belonging to this restaurant from JSON storage. A successful request has no response body.",
    responses={404: {"description": "Restaurant or menu item not found"}},
)
def delete_item(restaurant_id: int = Path(gt=0), item_id: int = Path(gt=0)) -> Response:
    try:
        service.delete_item(restaurant_id, item_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
