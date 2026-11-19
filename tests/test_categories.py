import json

from fastapi.testclient import TestClient

from app.main import app
from app.api.routers import category_routers, menu_routers
from app.repository.category_repo import CategoryRepository
from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.services.category_service import CategoryService
from tests.test_menus import make_menu_service

client = TestClient(app)


def make_category_service(tmp_path, monkeypatch):
    menu_service = make_menu_service(tmp_path)
    service = CategoryService(
        CategoryRepository(tmp_path / "menu_categories.json"),
        menu_service.repository,
        menu_service.restaurants,
    )
    monkeypatch.setattr(category_routers, "service", service)
    monkeypatch.setattr(menu_routers, "service", menu_service)
    return service


def test_existing_menu_categories(tmp_path, monkeypatch):
    make_category_service(tmp_path, monkeypatch)
    response = client.get("/restaurants/1/menu/categories")
    assert response.status_code == 200
    assert response.json() == ["mains", "drinks"]
    assert client.get("/restaurants/3/menu/categories").json() == []


def test_create_category_and_reload(tmp_path, monkeypatch):
    make_category_service(tmp_path, monkeypatch)
    response = client.post("/restaurants/1/menu/categories", json={"name": " Desserts "})
    assert response.status_code == 201
    assert response.json() == ["mains", "drinks", "Desserts"]
    fresh = CategoryService(
        CategoryRepository(tmp_path / "menu_categories.json"),
        MenuRepository(tmp_path / "menu_items.json"),
        RestaurantRepository(tmp_path / "restaurants.json"),
    )
    assert fresh.get_categories(1) == ["mains", "drinks", "Desserts"]
    assert fresh.get_categories(2) == ["mains"]


def test_duplicate_category_does_not_change_files(tmp_path, monkeypatch):
    make_category_service(tmp_path, monkeypatch)
    original = (tmp_path / "menu_items.json").read_text()
    response = client.post("/restaurants/1/menu/categories", json={"name": " MAINS "})
    assert response.status_code == 409
    assert not (tmp_path / "menu_categories.json").exists()
    assert (tmp_path / "menu_items.json").read_text() == original


def test_invalid_category_names(tmp_path, monkeypatch):
    make_category_service(tmp_path, monkeypatch)
    assert client.post("/restaurants/1/menu/categories", json={"name": " "}).status_code == 422
    assert client.post("/restaurants/1/menu/categories", json={"name": "x" * 81}).status_code == 422
    assert client.put("/restaurants/1/menu/categories", json={"name": "mains", "new_name": " "}).status_code == 422
    assert not (tmp_path / "menu_categories.json").exists()


def test_rename_updates_items_and_category_filter(tmp_path, monkeypatch):
    make_category_service(tmp_path, monkeypatch)
    response = client.put("/restaurants/1/menu/categories", json={"name": "MAINS", "new_name": "Specials"})
    assert response.status_code == 200
    assert response.json() == ["Specials", "drinks"]
    menu = client.get("/restaurants/1/menu", params={"category": "Specials"}).json()
    assert [item["name"] for item in menu["items"]] == ["Ramen"]
    assert client.get("/restaurants/1/menu", params={"category": "mains"}).json()["items"] == []
    saved = json.loads((tmp_path / "menu_items.json").read_text())
    assert saved[0]["category"] == "Specials"
    assert saved[2]["category"] == "mains"
    fresh = CategoryRepository(tmp_path / "menu_categories.json")
    assert fresh.get_by_restaurant(1) == ["Specials", "drinks"]


def test_cannot_rename_to_existing_category(tmp_path, monkeypatch):
    make_category_service(tmp_path, monkeypatch)
    original = (tmp_path / "menu_items.json").read_text()
    response = client.put("/restaurants/1/menu/categories", json={"name": "mains", "new_name": "DRINKS"})
    assert response.status_code == 409
    assert (tmp_path / "menu_items.json").read_text() == original
    assert not (tmp_path / "menu_categories.json").exists()


def test_cannot_delete_category_with_items(tmp_path, monkeypatch):
    make_category_service(tmp_path, monkeypatch)
    original = (tmp_path / "menu_items.json").read_text()
    response = client.request("DELETE", "/restaurants/1/menu/categories", json={"name": "mains"})
    assert response.status_code == 409
    assert (tmp_path / "menu_items.json").read_text() == original


def test_delete_empty_category_keeps_other_restaurants(tmp_path, monkeypatch):
    service = make_category_service(tmp_path, monkeypatch)
    client.post("/restaurants/1/menu/categories", json={"name": "desserts"})
    client.post("/restaurants/2/menu/categories", json={"name": "desserts"})
    response = client.request("DELETE", "/restaurants/1/menu/categories", json={"name": "DESSERTS"})
    assert response.status_code == 204
    assert response.content == b""
    assert service.categories.get_by_restaurant(1) == ["mains", "drinks"]
    assert service.categories.get_by_restaurant(2) == ["mains", "desserts"]


def test_missing_category_and_restaurant(tmp_path, monkeypatch):
    make_category_service(tmp_path, monkeypatch)
    assert client.get("/restaurants/99/menu/categories").status_code == 404
    assert client.post("/restaurants/99/menu/categories", json={"name": "desserts"}).status_code == 404
    assert client.put("/restaurants/1/menu/categories", json={"name": "unknown", "new_name": "desserts"}).status_code == 404
    assert client.request("DELETE", "/restaurants/1/menu/categories", json={"name": "unknown"}).status_code == 404
    assert not (tmp_path / "menu_categories.json").exists()
