from fastapi import APIRouter, HTTPException, Response, status

from app.repository.category_repo import CategoryRepository
from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.schema.category_schema import CategoryRequest, CategoryRename
from app.services.category_service import CategoryService

router = APIRouter(prefix="/restaurants/{restaurant_id}/menu/categories", tags=["categories"])
service = CategoryService(CategoryRepository(), MenuRepository(), RestaurantRepository())


@router.get("", response_model=list[str], summary="List menu categories")
def get_categories(restaurant_id: int) -> list[str]:
    try:
        return service.get_categories(restaurant_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("", response_model=list[str], status_code=status.HTTP_201_CREATED,
             summary="Create an empty menu category", responses={404: {}, 409: {}})
def create_category(restaurant_id: int, category: CategoryRequest) -> list[str]:
    try:
        return service.create_category(restaurant_id, category.name)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.put("", response_model=list[str], summary="Rename a category and its items",
            responses={404: {}, 409: {}})
def rename_category(restaurant_id: int, category: CategoryRename) -> list[str]:
    try:
        return service.rename_category(restaurant_id, category.name, category.new_name)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.delete("", status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete an empty category", responses={404: {}, 409: {}})
def delete_category(restaurant_id: int, category: CategoryRequest) -> Response:
    try:
        service.delete_category(restaurant_id, category.name)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
