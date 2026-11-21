from fastapi import APIRouter, Depends, HTTPException, Path

from app.api.dependencies import require_role, user_service
from app.api.routers.cart_routers import get_cart_service
from app.repository.orders_repo import OrderRepository
from app.schema.orders_schema import Order
from app.schema.users_schema import UserPublic
from app.services.checkout_service import CheckoutService
from app.services.orders_service import OrderService

router = APIRouter(tags=["orders"])
order_service = OrderService(OrderRepository())


def get_order_service() -> OrderService:
    return order_service


def get_checkout_service(
    carts=Depends(get_cart_service),
    orders: OrderService = Depends(get_order_service),
) -> CheckoutService:
    return CheckoutService(
        user_service, carts, carts.menu_service,
        carts.restaurant_repo, orders,
    )


@router.post(
    "/checkout", response_model=Order, status_code=201,
    summary="Checkout your cart",
    description="Validate the cart, save an order, then clear the cart.",
)
def checkout(
    user: UserPublic = Depends(require_role("customer")),
    service=Depends(get_checkout_service),
) -> Order:
    try:
        return service.checkout(user.id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Could not finish saving checkout. Check your orders before retrying.",
        )


@router.get("/orders", response_model=list[Order], summary="View your orders")
def get_orders(
    user: UserPublic = Depends(require_role("customer")),
    service: OrderService = Depends(get_order_service),
) -> list[Order]:
    return service.get_orders(user.id)


@router.get("/orders/{order_id}", response_model=Order, summary="View one of your orders")
def get_order(
    order_id: int = Path(gt=0),
    user: UserPublic = Depends(require_role("customer")),
    service: OrderService = Depends(get_order_service),
) -> Order:
    try:
        return service.get_order(user.id, order_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error))
