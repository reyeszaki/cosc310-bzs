from fastapi import APIRouter, HTTPException, Response, status

from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.schema.menu_schema import Menu, MenuItem, MenuItemCreate, MenuItemUpdate
from app.services.menu_service import MenuService

router = APIRouter(prefix="/restaurants/{restaurant_id}/menu", tags=["menus"])
repo = MenuRepository()
service = MenuService(repo, RestaurantRepository())


@router.get("", response_model=Menu)
def get_menu(restaurant_id: int, category: str | None = None) -> Menu:
    try:
        return service.get_menu(restaurant_id, category)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/items", response_model=MenuItem, status_code=status.HTTP_201_CREATED)
def add_item(restaurant_id: int, item: MenuItemCreate) -> MenuItem:
    try:
        return service.add_item(restaurant_id, item)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.put("/items/{item_id}", response_model=MenuItem)
def update_item(restaurant_id: int, item_id: int, item: MenuItemUpdate) -> MenuItem:
    try:
        return service.update_item(restaurant_id, item_id, item)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(restaurant_id: int, item_id: int) -> Response:
    try:
        service.delete_item(restaurant_id, item_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
