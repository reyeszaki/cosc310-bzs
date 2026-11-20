# GET cart
# POST adding items to cart
# UPDATE/PATCH/PUT the quantity of cart
# DELETE item in cart
# DELETE (to clear all items in cart)
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from app.schema.cart_schema import Cart, CartItemCreate, CartItemUpdate
from app.services.cart_service import CartService


router = APIRouter(prefix="/cart", tags=["cart"])


def get_current_customer_id() -> int:
    raise HTTPException(status_code=401, detail="Sign-in required")


def get_cart_service() -> CartService:
    raise HTTPException(status_code=503, detail="Cart service is not configured")


CustomerID = Annotated[int, Depends(get_current_customer_id)]
Service = Annotated[CartService, Depends(get_cart_service)]
MenuItemID = Annotated[int, Path(gt=0)]


@router.get("", response_model=Cart)
def get_cart(customer_id: CustomerID, service: Service) -> Cart:
    return service.get_or_create_cart(customer_id)


@router.post("/items", response_model=Cart, status_code=201)
def add_item(
    request: CartItemCreate, customer_id: CustomerID, service: Service
) -> Cart:
    try:
        return service.add_item(customer_id, request)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.patch("/items/{menu_item_id}", response_model=Cart)
def update_quantity(
    menu_item_id: MenuItemID,
    request: CartItemUpdate,
    customer_id: CustomerID,
    service: Service,
) -> Cart:
    try:
        return service.update_quantity(customer_id, menu_item_id, request)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/items/{menu_item_id}", response_model=Cart)
def remove_item(
    menu_item_id: MenuItemID, customer_id: CustomerID, service: Service
) -> Cart:
    try:
        return service.remove_item(customer_id, menu_item_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/items", response_model=Cart)
def clear_cart(customer_id: CustomerID, service: Service) -> Cart:
    return service.clear_cart(customer_id)