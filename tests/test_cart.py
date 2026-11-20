from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routers import cart_routers
from app.repository.cart_repo import CartRepository
from app.services.cart_service import CartService

class SampleMenuService:
    def get_menu(self, restaurant_id):
        menus = {
            2: [
                SimpleNamespace(
                    id=7, name="Burger", price=Decimal("8.50"), is_available=True
                ),
                SimpleNamespace(
                    id=8, name="Fries", price=Decimal("4.00"), is_available=False
                ),
            ],
            3: [
                SimpleNamespace(
                    id=9, name="Pizza", price=Decimal("12.00"), is_available=True
                ),
            ],
        }
        return SimpleNamespace(items=menus.get(restaurant_id, []))


@pytest.fixture(name="client")
def client(tmp_path):
    def require_active_customer(customer_id):
        assert customer_id == 5

    service = CartService(
        CartRepository(tmp_path / "carts.json"),
        SampleMenuService(),
        require_active_customer,
    )

    app = FastAPI()
    app.include_router(cart_routers.router)
    app.dependency_overrides[cart_routers.get_current_customer_id] = lambda: 5
    app.dependency_overrides[cart_routers.get_cart_service] = lambda: service

    with TestClient(app) as test_client:
        yield test_client

def add_item(client):
    return client.post(
        "/cart/items",
        json={"restaurant_id": 2, "menu_item_id": 7, "quantity": 2},
    )

def test_get_cart(client):
    response = client.get("/cart")

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert Decimal(response.json()["total"]) == Decimal("0.00")


def test_delete_item_from_cart(client):
    assert add_item(client).status_code == 201

    response = client.delete("/cart/items/7")

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["restaurant_id"] is None


def test_add_item_to_cart(client):
    response = add_item(client)

    assert response.status_code == 201
    cart = response.json()
    assert cart["items"][0]["menu_item_id"] == 7
    assert cart["items"][0]["quantity"] == 2
    assert Decimal(cart["total"]) == Decimal("17.00")


def test_delete_all_from_cart(client):
    assert add_item(client).status_code == 201

    response = client.delete("/cart/items")

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["restaurant_id"] is None
    assert Decimal(response.json()["total"]) == Decimal("0.00")


def test_update_item_quantity(client):
    assert add_item(client).status_code == 201

    response = client.patch("/cart/items/7", json={"quantity": 3})

    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 3
    assert Decimal(response.json()["total"]) == Decimal("25.50")


def test_delete_item_from_empty_cart(client):
    response = client.delete("/cart/items/7")

    assert response.status_code == 404


def test_update_invalid_item_quantity(client):
    assert add_item(client).status_code == 201

    response = client.patch("/cart/items/7", json={"quantity": 0})

    assert response.status_code == 422
    assert client.get("/cart").json()["items"][0]["quantity"] == 2


def test_add_nonexistent_item_to_cart(client):
    response = client.post(
        "/cart/items",
        json={"restaurant_id": 2, "menu_item_id": 999},
    )

    assert response.status_code == 404


def test_add_unavailable_item_to_cart(client):
    response = client.post(
        "/cart/items",
        json={"restaurant_id": 2, "menu_item_id": 8},
    )

    assert response.status_code == 409


def test_add_item_from_different_restaurant(client):
    original_cart = add_item(client)
    assert original_cart.status_code == 201

    response = client.post(
        "/cart/items",
        json={"restaurant_id": 3, "menu_item_id": 9},
    )

    assert response.status_code == 409
    assert client.get("/cart").json() == original_cart.json()
