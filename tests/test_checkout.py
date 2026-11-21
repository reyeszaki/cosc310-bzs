import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import dependencies
from app.api.routers import cart_routers, orders_routers
from app.repository.cart_repo import CartRepository
from app.repository.menu_repo import MenuRepository
from app.repository.orders_repo import OrderRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.repository.users_repo import UserRepository
from app.services.cart_service import CartService
from app.services.menu_service import MenuService
from app.services.orders_service import OrderService


@pytest.fixture
def setup_checkout(tmp_path, monkeypatch):
    monkeypatch.setattr(dependencies.user_service, "repository", UserRepository(tmp_path / "users.json"))
    monkeypatch.setattr(dependencies.user_service, "_sessions", {})
    (tmp_path / "restaurants.json").write_text(json.dumps([
        {"id": 1, "name": "Cafe", "cuisine": "Cafe", "address": "1 St", "is_open": True},
    ]))
    (tmp_path / "menu.json").write_text(json.dumps([
        {"id": 1, "restaurant_id": 1, "name": "Tea", "description": "Tea",
         "price": 3.10, "category": "drinks", "is_available": True},
    ]))
    restaurants = RestaurantRepository(tmp_path / "restaurants.json")
    menu_repo = MenuRepository(tmp_path / "menu.json")
    cart_repo = CartRepository(tmp_path / "carts.json")
    order_repo = OrderRepository(tmp_path / "orders.json")

    carts = CartService(
        cart_repo,
        MenuService(menu_repo, restaurants),
        dependencies.user_service.require_active,
        restaurants,
    )
    orders = OrderService(order_repo)
    monkeypatch.setattr(cart_routers, "cart_service", carts)
    monkeypatch.setattr(orders_routers, "order_service", orders)

    with TestClient(app) as test_client:
        user = {"name": "Ana", "last_name": "Lee", "email": "ana@example.ca", "password": "secret123"}
        assert test_client.post("/users", json=user).status_code == 201
        token = test_client.post(
            "/auth/login", json={"email": user["email"], "password": user["password"]}
        ).json()["access_token"]
        headers = {"Authorization": "Bearer " + token}
        assert test_client.put("/users/me", headers=headers, json={"address": "12 Home St"}).status_code == 200
        assert test_client.post(
            "/cart/items", headers=headers, json={"restaurant_id": 1, "menu_item_id": 1, "quantity": 2}
        ).status_code == 201
        yield test_client, tmp_path, headers, carts, orders, menu_repo, cart_repo, order_repo


def test_checkout_saves_and_clears_cart(setup_checkout):
    client, folder, headers, carts, orders, _, cart_repo, order_repo = setup_checkout
    response = client.post("/checkout", headers=headers)
    assert response.status_code == 201
    order = response.json()
    assert order["total"] == 6.20
    assert order["status"] == "Placed"
    assert order["delivery_address"] == "12 Home St"
    assert cart_repo.get_by_customer(1)["items"] == []
    assert client.get("/orders", headers=headers).json() == [order]
    assert client.get(f"/orders/{order['id']}", headers=headers).json() == order
    fresh = OrderService(OrderRepository(folder / "orders.json"))
    assert fresh.get_order(1, order["id"]).model_dump() == order
    assert client.post("/checkout", headers=headers).status_code == 409
    assert len(order_repo.get_all()) == 1


def test_checkout_refreshes_price_and_saves_snapshot(setup_checkout):
    client, folder, headers, carts, orders, menu_repo, _, _ = setup_checkout
    items = menu_repo.get_all()
    items[0]["price"] = 4.25
    menu_repo.save(items)
    order = client.post("/checkout", headers=headers).json()
    assert order["total"] == 8.50
    items[0]["price"] = 9.00
    items[0]["name"] = "New Tea"
    menu_repo.save(items)
    client.put("/users/me", headers=headers, json={"address": "New Address"})
    saved = client.get(f"/orders/{order['id']}", headers=headers).json()
    assert saved["items"][0]["name"] == "Tea"
    assert saved["total"] == 8.50
    assert saved["delivery_address"] == "12 Home St"


def test_unavailable_item_leaves_cart_unchanged(setup_checkout):
    client, folder, headers, carts, orders, menu_repo, _, order_repo = setup_checkout
    original = (folder / "carts.json").read_text()
    items = menu_repo.get_all()
    items[0]["is_available"] = False
    menu_repo.save(items)
    assert client.post("/checkout", headers=headers).status_code == 409
    assert (folder / "carts.json").read_text() == original
    assert order_repo.get_all() == []


def test_closed_restaurant_and_deleted_item(setup_checkout):
    client, folder, headers, carts, orders, menu_repo, cart_repo, order_repo = setup_checkout
    restaurants = json.loads((folder / "restaurants.json").read_text())
    restaurants[0]["is_open"] = False
    (folder / "restaurants.json").write_text(json.dumps(restaurants))
    assert client.post("/checkout", headers=headers).status_code == 409
    restaurants[0]["is_open"] = True
    (folder / "restaurants.json").write_text(json.dumps(restaurants))
    menu_repo.save([])
    assert client.post("/checkout", headers=headers).status_code == 404
    assert len(cart_repo.get_by_customer(1)["items"]) == 1
    assert order_repo.get_all() == []


def test_missing_address_and_invalid_quantity(setup_checkout):
    client, folder, headers, carts, orders, _, cart_repo, order_repo = setup_checkout
    dependencies.user_service.repository.update(1, {"address": " "})
    assert client.post("/checkout", headers=headers).status_code == 409
    dependencies.user_service.repository.update(1, {"address": "12 Home St"})
    cart = cart_repo.get_by_customer(1)
    cart["items"][0]["quantity"] = 0
    cart_repo.save(cart)
    assert client.post("/checkout", headers=headers).status_code == 409
    assert order_repo.get_all() == []


def test_failed_save_keeps_cart(setup_checkout, monkeypatch):
    client, folder, headers, carts, orders, _, _, order_repo = setup_checkout
    original = (folder / "carts.json").read_text()

    def fail_save(fields):
        raise OSError("Disk full")

    monkeypatch.setattr(order_repo, "create", fail_save)
    assert client.post("/checkout", headers=headers).status_code == 500
    assert (folder / "carts.json").read_text() == original
    assert order_repo.get_all() == []


def test_authentication_and_order_ownership(setup_checkout):
    client, folder, headers, carts, orders, _, _, _ = setup_checkout
    order = client.post("/checkout", headers=headers).json()
    assert client.post("/checkout").status_code == 401
    assert client.get("/orders").status_code == 401
    client.post("/users", json={"name": "Bob", "last_name": "Lee", "email": "bob@example.ca", "password": "secret123"})
    token = client.post("/auth/login", json={"email": "bob@example.ca", "password": "secret123"}).json()["access_token"]
    other = {"Authorization": "Bearer " + token}
    assert client.get("/orders", headers=other).json() == []
    assert client.get(f"/orders/{order['id']}", headers=other).status_code == 404
    dependencies.user_service.repository.update(1, {"role": "owner"})
    assert client.post("/checkout", headers=headers).status_code == 403
    dependencies.user_service.repository.update(1, {"role": "customer", "is_active": False})
    assert client.post("/checkout", headers=headers).status_code == 401


def test_clear_failure_keeps_saved_order(setup_checkout, monkeypatch):
    client, folder, headers, carts, orders, _, cart_repo, order_repo = setup_checkout

    def fail_clear(customer_id):
        raise OSError("Cannot clear cart")

    monkeypatch.setattr(carts, "clear_cart", fail_clear)
    assert client.post("/checkout", headers=headers).status_code == 500
    assert len(order_repo.get_all()) == 1
    assert len(cart_repo.get_by_customer(1)["items"]) == 1
