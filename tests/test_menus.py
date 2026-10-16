import json
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routers.menu_routers import get_menu_service
from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.services.menu_service import MenuService


@pytest.fixture
def menu_client(tmp_path):
    restaurant_file = tmp_path / "restaurants.json"
    restaurant_file.write_text(json.dumps([
        {"id": 1}, {"id": 2}, {"id": 3}
    ]))
    menu_file = tmp_path / "menus.json"
    menu_file.write_text(json.dumps([
        {"id": 1, "restaurant_id": 1, "name": "Ramen", "description": "Noodles",
         "price": 12.50, "category": "mains", "is_available": True},
        {"id": 2, "restaurant_id": 1, "name": "Tea", "description": "Green tea",
         "price": 3, "category": "drinks", "is_available": False},
        {"id": 3, "restaurant_id": 2, "name": "Pizza", "description": "Cheese",
         "price": 15, "category": "mains", "is_available": True}
    ]))
    service = MenuService(MenuRepository(menu_file), RestaurantRepository(restaurant_file))
    app.dependency_overrides[get_menu_service] = lambda: service
    # Always remove the override, including when a test fails.
    try:
        with TestClient(app) as client:
            yield client, menu_file, restaurant_file
    finally:
        app.dependency_overrides.pop(get_menu_service, None)


NEW_ITEM = {"name": "Mochi", "description": "Rice cake", "price": 4.50, "category": "desserts"}


def test_view_and_filter_menu(menu_client):
    client, _, _ = menu_client
    response = client.get("/restaurants/1/menu")
    assert response.status_code == 200
    data = response.json()
    assert data["restaurant_id"] == 1
    assert [item["name"] for item in data["items"]] == ["Ramen", "Tea"]
    assert data["items"][0]["description"] == "Noodles"
    assert data["items"][0]["price"] == 12.50
    assert data["items"][1]["is_available"] is False
    assert len(client.get("/restaurants/1/menu", params={"category": " MAINS "}).json()["items"]) == 1
    assert client.get("/restaurants/1/menu?category=unknown").json()["items"] == []
    assert len(client.get("/restaurants/1/menu?category=").json()["items"]) == 2
    assert client.get("/restaurants/3/menu").json()["items"] == []


def test_add_update_and_persist_after_recreating_service(menu_client):
    client, menu_file, restaurant_file = menu_client
    response = client.post("/restaurants/1/menu/items", json=NEW_ITEM)
    assert response.status_code == 201
    item = response.json()
    assert item["restaurant_id"] == 1
    assert item["is_available"] is True
    assert item["id"] not in [1, 2, 3]
    path = f"/restaurants/1/menu/items/{item['id']}"
    response = client.patch(path, json={"price": 5.25, "category": "specials", "is_available": False})
    assert response.status_code == 200
    assert response.json()["name"] == "Mochi"
    assert response.json()["price"] == 5.25
    assert response.json()["category"] == "specials"
    assert response.json()["is_available"] is False
    fresh = MenuService(MenuRepository(menu_file), RestaurantRepository(restaurant_file))
    app.dependency_overrides[get_menu_service] = lambda: fresh
    stored = client.get("/restaurants/1/menu?category=specials").json()["items"][0]
    assert stored == response.json()
    assert client.patch(path, json={"is_available": True}).json()["is_available"] is True


def test_update_all_fields_and_trim_text(menu_client):
    client, _, _ = menu_client
    response = client.patch("/restaurants/1/menu/items/1", json={
        "name": " New name ", "description": " New description ", "price": 9.99,
        "category": " desserts ", "is_available": False
    })
    assert response.status_code == 200
    assert response.json() == {
        "id": 1, "restaurant_id": 1, "name": "New name", "description": "New description",
        "price": 9.99, "category": "desserts", "is_available": False
    }


@pytest.mark.parametrize("change", [
    {"price": 0}, {"price": -1}, {"price": "NaN"}, {"price": "Infinity"},
    {"price": 1.234}, {"price": "not a price"}, {"name": " "},
    {"description": ""}, {"category": " "}, {"is_available": "invalid"},
    {"id": 99}, {"restaurant_id": 2}
])
def test_invalid_create_and_patch_do_not_write(menu_client, change):
    client, menu_file, _ = menu_client
    original = menu_file.read_bytes()
    assert client.post("/restaurants/1/menu/items", json={**NEW_ITEM, **change}).status_code == 422
    assert client.patch("/restaurants/1/menu/items/1", json=change).status_code == 422
    assert menu_file.read_bytes() == original


@pytest.mark.parametrize("patch", [{}, {"name": None}, {"description": None},
    {"price": None}, {"category": None}, {"is_available": None}])
def test_empty_and_null_patch_rejected(menu_client, patch):
    client, _, _ = menu_client
    assert client.patch("/restaurants/1/menu/items/1", json=patch).status_code == 422


def test_missing_restaurants_items_and_cross_restaurant_access(menu_client):
    client, menu_file, _ = menu_client
    original = menu_file.read_bytes()
    assert client.get("/restaurants/99/menu").status_code == 404
    assert client.post("/restaurants/99/menu/items", json=NEW_ITEM).status_code == 404
    for path in ["/restaurants/99/menu/items/1", "/restaurants/1/menu/items/99", "/restaurants/1/menu/items/3"]:
        assert client.patch(path, json={"price": 9}).status_code == 404
        assert client.delete(path).status_code == 404
    assert menu_file.read_bytes() == original


def test_delete_is_immediate_and_persistent(menu_client):
    client, menu_file, restaurant_file = menu_client
    response = client.delete("/restaurants/1/menu/items/1")
    assert response.status_code == 204
    assert response.content == b""
    fresh = MenuService(MenuRepository(menu_file), RestaurantRepository(restaurant_file))
    assert [item.id for item in fresh.get_menu(1).items] == [2]
    assert [item.id for item in fresh.get_menu(2).items] == [3]
    assert client.delete("/restaurants/1/menu/items/1").status_code == 404


def test_missing_menu_file_initializes_on_add(tmp_path):
    repository = MenuRepository(tmp_path / "nested" / "menu.json")
    assert repository.get_all() == []
    saved = repository.add({**NEW_ITEM, "restaurant_id": 1, "is_available": True})
    assert MenuRepository(repository.data_path).get_all() == [saved]


def test_positive_ids_and_required_create_fields(menu_client):
    client, _, _ = menu_client
    assert client.get("/restaurants/0/menu").status_code == 422
    assert client.patch("/restaurants/1/menu/items/0", json={"price": 2}).status_code == 422
    assert client.post("/restaurants/1/menu/items", json={"name": "Incomplete"}).status_code == 422


def test_openapi_documents_menu_contract():
    schema = app.openapi()
    assert schema["paths"]["/restaurants/{restaurant_id}/menu/items"]["post"]["responses"].keys() >= {"201", "404", "422"}
    assert "patch" in schema["paths"]["/restaurants/{restaurant_id}/menu/items/{item_id}"]



def test_changes_survive_a_new_python_process(menu_client):
    client, menu_file, restaurant_file = menu_client
    created = client.post("/restaurants/1/menu/items", json=NEW_ITEM).json()
    client.patch(
        f"/restaurants/1/menu/items/{created['id']}",
        json={"price": 7.50, "is_available": False},
    ).raise_for_status()
    # A separate Python process cannot read the first process's in-memory objects.
    script = """
import sys
from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.services.menu_service import MenuService
service = MenuService(MenuRepository(sys.argv[1]), RestaurantRepository(sys.argv[2]))
print(service.get_menu(1).model_dump_json())
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(menu_file), str(restaurant_file)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True, text=True, check=True, timeout=10,
    )
    items = json.loads(result.stdout)["items"]
    saved = next(item for item in items if item["id"] == created["id"])
    assert saved["name"] == "Mochi"
    assert saved["price"] == 7.50
    assert saved["is_available"] is False


def test_failed_file_replace_preserves_stored_menu(tmp_path, monkeypatch):
    menu_file = tmp_path / "menu.json"
    repository = MenuRepository(menu_file)
    repository.add({**NEW_ITEM, "restaurant_id": 1, "is_available": True})
    original = menu_file.read_bytes()

    def fail_replace(source, destination):
        raise OSError("Simulated disk failure")

    monkeypatch.setattr("app.repository.menu_repo.os.replace", fail_replace)
    with pytest.raises(OSError, match="Simulated disk failure"):
        repository.update(1, 1, {"price": 6.50})
    assert menu_file.read_bytes() == original
    assert list(tmp_path.iterdir()) == [menu_file]


def test_api_documentation_explains_parameters_and_errors(menu_client):
    client, _, _ = menu_client
    assert client.get("/docs").status_code == 200
    schema = client.get("/openapi.json").json()
    menu = schema["paths"]["/restaurants/{restaurant_id}/menu"]["get"]
    parameters = {parameter["name"]: parameter for parameter in menu["parameters"]}
    assert "blank" in parameters["category"]["description"]
    assert parameters["restaurant_id"]["schema"]["exclusiveMinimum"] == 0
    assert menu["responses"]["404"]["content"]["application/json"]["schema"]["$ref"].endswith("/MenuError")
    assert "422" in menu["responses"]
    patch = schema["paths"]["/restaurants/{restaurant_id}/menu/items/{item_id}"]["patch"]
    assert "Omitted fields remain unchanged" in patch["description"]
    assert patch["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith("/MenuItemUpdate")


@pytest.mark.parametrize("field", ["name", "description", "price", "category"])
def test_each_create_field_is_required(menu_client, field):
    client, menu_file, _ = menu_client
    payload = {key: value for key, value in NEW_ITEM.items() if key != field}
    original = menu_file.read_bytes()
    response = client.post("/restaurants/1/menu/items", json=payload)
    assert response.status_code == 422
    assert any(error["loc"][-1] == field for error in response.json()["detail"])
    assert menu_file.read_bytes() == original
