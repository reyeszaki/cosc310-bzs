import json

from fastapi.testclient import TestClient

from app.main import app
from app.api.routers import menu_routers
from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.services.menu_service import MenuService

client = TestClient(app)

NEW_ITEM = {
    "name": "Mochi",
    "description": "Rice cake",
    "price": 4.50,
    "category": "desserts",
    "is_available": True,
}


def make_menu_service(tmp_path):
    # Each test uses its own files, just like the restaurant tests.
    restaurant_file = tmp_path / "restaurants.json"
    restaurant_file.write_text(json.dumps([
        {"id": 1, "name": "Ramen Shop", "cuisine": "Japanese", "address": "1 Main St", "is_open": True},
        {"id": 2, "name": "Pizza Shop", "cuisine": "Italian", "address": "2 Main St", "is_open": True},
        {"id": 3, "name": "New Cafe", "cuisine": "Cafe", "address": "3 Main St", "is_open": True},
    ]))
    menu_file = tmp_path / "menu_items.json"
    menu_file.write_text(json.dumps([
        {"id": 1, "restaurant_id": 1, "name": "Ramen", "description": "Noodles",
         "price": 12.50, "category": "mains", "is_available": True},
        {"id": 2, "restaurant_id": 1, "name": "Tea", "description": "Green tea",
         "price": 3, "category": "drinks", "is_available": False},
        {"id": 3, "restaurant_id": 2, "name": "Pizza", "description": "Cheese",
         "price": 15, "category": "mains", "is_available": True},
    ]))
    return MenuService(MenuRepository(menu_file), RestaurantRepository(restaurant_file))


def test_get_menu(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    response = client.get("/restaurants/1/menu")
    assert response.status_code == 200
    data = response.json()
    assert data["restaurant_id"] == 1
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "Ramen"
    assert data["items"][0]["price"] == 12.50
    assert data["items"][1]["is_available"] is False


def test_filter_menu_by_category(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    response = client.get("/restaurants/1/menu", params={"category": " DRINKS "})
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["name"] == "Tea"


def test_menu_category_no_match(tmp_path):
    service = make_menu_service(tmp_path)
    assert service.get_menu(1, "unknown").items == []


def test_blank_category_returns_all_items(tmp_path):
    service = make_menu_service(tmp_path)
    assert len(service.get_menu(1, " ").items) == 2


def test_restaurant_with_empty_menu(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    response = client.get("/restaurants/3/menu")
    assert response.status_code == 200
    assert response.json() == {"restaurant_id": 3, "items": []}


def test_add_menu_item(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    response = client.post("/restaurants/1/menu/items", json=NEW_ITEM)
    expected = {**NEW_ITEM, "id": 4, "restaurant_id": 1}
    assert response.status_code == 201
    assert response.json() == expected
    saved_items = json.loads((tmp_path / "menu_items.json").read_text())
    assert saved_items[-1] == expected


def test_update_menu_item(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    updated = {
        "name": "Updated Ramen",
        "description": "Spicy noodles",
        "price": 14.25,
        "category": "specials",
        "is_available": False,
    }
    response = client.put("/restaurants/1/menu/items/1", json=updated)
    expected = {**updated, "id": 1, "restaurant_id": 1}
    assert response.status_code == 200
    assert response.json() == expected
    saved_items = json.loads((tmp_path / "menu_items.json").read_text())
    assert saved_items[0] == expected


def test_delete_menu_item(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    response = client.delete("/restaurants/1/menu/items/1")
    assert response.status_code == 204
    assert response.content == b""
    saved_items = json.loads((tmp_path / "menu_items.json").read_text())
    assert len(saved_items) == 2
    assert saved_items[0]["id"] == 2


def test_missing_restaurant(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    assert client.get("/restaurants/99/menu").status_code == 404
    assert client.post("/restaurants/99/menu/items", json=NEW_ITEM).status_code == 404
    assert client.put("/restaurants/99/menu/items/1", json=NEW_ITEM).status_code == 404
    assert client.delete("/restaurants/99/menu/items/1").status_code == 404


def test_update_missing_item(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    response = client.put("/restaurants/1/menu/items/99", json=NEW_ITEM)
    assert response.status_code == 404


def test_delete_missing_item(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    response = client.delete("/restaurants/1/menu/items/99")
    assert response.status_code == 404


def test_cannot_change_another_restaurants_item(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    original = (tmp_path / "menu_items.json").read_text()
    assert client.put("/restaurants/1/menu/items/3", json=NEW_ITEM).status_code == 404
    assert client.delete("/restaurants/1/menu/items/3").status_code == 404
    assert (tmp_path / "menu_items.json").read_text() == original


def test_invalid_menu_price(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    invalid = {**NEW_ITEM, "price": 0}
    original = (tmp_path / "menu_items.json").read_text()
    assert client.post("/restaurants/1/menu/items", json=invalid).status_code == 422
    assert client.put("/restaurants/1/menu/items/1", json=invalid).status_code == 422
    assert (tmp_path / "menu_items.json").read_text() == original


def test_blank_menu_name(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    response = client.post("/restaurants/1/menu/items", json={**NEW_ITEM, "name": " "})
    assert response.status_code == 422


def test_update_requires_all_fields(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    original = (tmp_path / "menu_items.json").read_text()
    response = client.put("/restaurants/1/menu/items/1", json={"price": 5.25})
    assert response.status_code == 422
    assert (tmp_path / "menu_items.json").read_text() == original


def test_cannot_change_item_ids(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    response = client.put("/restaurants/1/menu/items/1", json={**NEW_ITEM, "restaurant_id": 2})
    assert response.status_code == 422


def test_changes_remain_after_reloading_files(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    added = client.post("/restaurants/1/menu/items", json=NEW_ITEM).json()
    updated = {**NEW_ITEM, "price": 5.25, "is_available": False}
    response = client.put(f"/restaurants/1/menu/items/{added['id']}", json=updated)
    assert response.status_code == 200
    # New repository/service objects read the saved files, not the previous objects.
    fresh = MenuService(
        MenuRepository(tmp_path / "menu_items.json"),
        RestaurantRepository(tmp_path / "restaurants.json"),
    )
    saved_item = fresh.get_menu(1).items[-1]
    assert saved_item.price == 5.25
    assert saved_item.is_available is False


def test_missing_menu_file(tmp_path):
    repository = MenuRepository(tmp_path / "new_menu.json")
    assert repository.get_all() == []
    repository.add({**NEW_ITEM, "restaurant_id": 1})
    assert len(MenuRepository(tmp_path / "new_menu.json").get_all()) == 1


def test_menu_update_uses_put(tmp_path, monkeypatch):
    service = make_menu_service(tmp_path)
    monkeypatch.setattr(menu_routers, "service", service)
    schema = client.get("/openapi.json").json()
    item_route = schema["paths"]["/restaurants/{restaurant_id}/menu/items/{item_id}"]
    assert "put" in item_route
    assert "patch" not in item_route
    response = client.put("/restaurants/1/menu/items/1", json=NEW_ITEM)
    assert response.status_code == 200
