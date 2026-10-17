"""Exercise the shared restaurant/menu contract, including real HTTP server restarts."""
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.routers.menu_routers import get_menu_service
from app.api.routers import restaurant_routers
from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.services.menu_service import MenuService
from app.services.restaurant_service import RestaurantService

RESTAURANT = {"name": " New Cafe ", "cuisine": " Cafe ", "address": " 10 Main St ", "is_open": True}
ITEM = {"name": "Tea", "description": "Hot tea", "price": 3.25, "category": " drinks "}


@pytest.fixture
def files(tmp_path):
    restaurants = tmp_path / "restaurants.json"
    menus = tmp_path / "menu_items.json"
    restaurants.write_text("[]")
    return restaurants, menus


@pytest.fixture
def client(files, monkeypatch):
    restaurants, menus = files
    repository = RestaurantRepository(restaurants)
    monkeypatch.setattr(restaurant_routers, "service", RestaurantService(repository, MenuRepository(menus)))
    app.dependency_overrides[get_menu_service] = lambda: MenuService(MenuRepository(menus), repository)
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_menu_service, None)


def create_flow(client):
    assert client.get("/restaurants").json() == []
    response = client.post("/restaurants", json=RESTAURANT)
    assert response.status_code == 201
    restaurant = response.json()
    rid = restaurant["id"]
    assert restaurant == {"id": rid, "name": "New Cafe", "cuisine": "Cafe", "address": "10 Main St", "is_open": True}
    path = f"/restaurants/{rid}"
    assert client.get(path).json() == restaurant
    assert client.get(path + "/menu").json() == {"restaurant_id": rid, "items": []}
    response = client.put(path, json={**RESTAURANT, "name": "Updated Cafe", "is_open": False})
    assert response.status_code == 200
    restaurant = response.json()
    assert restaurant["address"] == "10 Main St"
    response = client.get("/restaurants", params={"search": " UPDATED ", "cuisine": " CAFE ", "is_open": False})
    assert response.status_code == 200
    assert response.json() == [restaurant]
    assert client.get("/restaurants", params={"is_open": True}).json() == []
    response = client.post(path + "/menu/items", json=ITEM)
    assert response.status_code == 201
    item = response.json()
    assert item["restaurant_id"] == rid
    response = client.patch(path + f"/menu/items/{item['id']}", json={"price": 4.5, "is_available": False})
    assert response.status_code == 200
    item = response.json()
    assert item["name"] == "Tea"
    assert item["price"] == 4.5
    assert item["is_available"] is False
    assert client.get(path + "/menu", params={"category": " DRINKS "}).json()["items"] == [item]
    assert client.get(path + "/menu?category=mains").json()["items"] == []
    # A second restaurant must neither inherit nor mutate the first one's menu.
    other = client.post("/restaurants", json={**RESTAURANT, "name": "Other"}).json()
    assert other["id"] != rid
    assert client.get(f"/restaurants/{other['id']}/menu").json()["items"] == []
    assert client.patch(f"/restaurants/{other['id']}/menu/items/{item['id']}", json={"price": 9}).status_code == 404
    return restaurant, item


def test_connected_flow(client):
    create_flow(client)


@pytest.mark.parametrize("payload", [{}, {"name": None}, {"cuisine": " "}, {"address": ""}, {"id": 9}, {"is_open": "maybe"}, {"unknown": "x"}])
def test_restaurant_put_rejects_invalid_input_without_writing(client, files, payload):
    rid = client.post("/restaurants", json=RESTAURANT).json()["id"]
    original = files[0].read_bytes()
    assert client.put(f"/restaurants/{rid}", json={**RESTAURANT, **payload} if payload else {}).status_code == 422
    assert files[0].read_bytes() == original


@pytest.mark.parametrize("payload", [{}, {"name": " "}, {**RESTAURANT, "id": 9}, {**RESTAURANT, "cuisine": None}, {**RESTAURANT, "is_open": "maybe"}])
def test_restaurant_create_rejects_invalid_input(client, files, payload):
    assert client.post("/restaurants", json=payload).status_code == 422
    assert files[0].read_text() == "[]"


def test_restaurant_errors_and_openapi(client):
    assert client.get("/restaurants/99").status_code == 404
    assert client.put("/restaurants/99", json=RESTAURANT).status_code == 404
    assert client.get("/restaurants/0").status_code == 422
    assert client.put("/restaurants/-1", json=RESTAURANT).status_code == 422
    assert client.get("/restaurants?is_open=maybe").status_code == 422
    paths = client.get("/openapi.json").json()["paths"]
    assert paths["/restaurants"]["post"]["responses"].keys() >= {"201", "422"}
    assert paths["/restaurants/{restaurant_id}"]["put"]["responses"].keys() >= {"200", "404", "422"}


SERVER = """
import sys
import uvicorn
from app.main import app
from app.api.routers import restaurant_routers
from app.api.routers.menu_routers import get_menu_service
from app.repository.restaurant_repo import RestaurantRepository
from app.repository.menu_repo import MenuRepository
from app.services.restaurant_service import RestaurantService
from app.services.menu_service import MenuService
restaurants = RestaurantRepository(sys.argv[1])
restaurant_routers.service = RestaurantService(restaurants, MenuRepository(sys.argv[2]))
app.dependency_overrides[get_menu_service] = lambda: MenuService(MenuRepository(sys.argv[2]), restaurants)
uvicorn.run(app, host="127.0.0.1", port=int(sys.argv[3]), log_level="error")
"""


@contextmanager
def live_server(files):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen(
        [sys.executable, "-c", SERVER, *map(str, files), str(port)],
        cwd=Path(__file__).resolve().parents[1], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True,
    )
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=2, trust_env=False) as client:
            deadline = time.monotonic() + 10
            while True:
                if process.poll() is not None:
                    raise AssertionError(f"Server exited: {process.communicate()}")
                try:
                    if client.get("/health").status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                if time.monotonic() >= deadline:
                    raise AssertionError("Server did not become ready")
                time.sleep(0.05)
            yield client
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate(timeout=5)


def test_http_flow_survives_application_restart(files):
    with live_server(files) as client:
        restaurant, item = create_flow(client)
        assert client.get("/docs").status_code == 200
        assert client.get("/").status_code == 200
        assert "async function loadRestaurants" in client.get("/app.js").text
    # Both services and the ASGI application live in a completely new process.
    with live_server(files) as client:
        path = f"/restaurants/{restaurant['id']}"
        assert client.get(path).json() == restaurant
        assert client.get("/restaurants", params={"search": "updated", "is_open": False}).json() == [restaurant]
        assert client.get(path + "/menu").json() == {"restaurant_id": restaurant["id"], "items": [item]}
        assert client.get(path + "/menu?category=DRINKS").json()["items"] == [item]


def test_failed_replace_preserves_restaurants(files, monkeypatch):
    repository = RestaurantRepository(files[0])
    restaurant = repository.create({"name": "Cafe", "cuisine": "Cafe", "address": "Street", "is_open": True})
    original = files[0].read_bytes()

    def fail_replace(*args):
        raise OSError("Simulated disk failure")

    monkeypatch.setattr("app.repository.restaurant_repo.os.replace", fail_replace)
    with pytest.raises(OSError, match="Simulated disk failure"):
        repository.update(restaurant["id"], {"name": "Lost"})
    assert files[0].read_bytes() == original
    assert list(files[0].parent.iterdir()) == [files[0]]


def test_default_data_and_registered_routes_agree():
    """Read the committed data through production dependencies without changing it."""
    with TestClient(app) as client:
        response = client.get("/restaurants")
        assert response.status_code == 200
        restaurants = response.json()
        ids = [row["id"] for row in restaurants]
        assert len(ids) == len(set(ids))
        stored_items = MenuRepository().get_all()
        assert len({row["id"] for row in stored_items}) == len(stored_items)
        assert all(row["restaurant_id"] in ids for row in stored_items)
        for restaurant in restaurants:
            path = f"/restaurants/{restaurant['id']}"
            assert client.get(path).json() == restaurant
            response = client.get(path + "/menu")
            assert response.status_code == 200
            assert response.json()["items"] == [row for row in stored_items if row["restaurant_id"] == restaurant["id"]]


def test_delete_cannot_orphan_or_reassign_menu_items(client):
    restaurant, item = create_flow(client)
    path = f"/restaurants/{restaurant['id']}"
    response = client.delete(path)
    assert response.status_code == 409
    assert "menu items" in response.json()["detail"]
    assert client.get(path).status_code == 200
    assert client.delete(path + f"/menu/items/{item['id']}").status_code == 204
    assert client.delete(path).status_code == 200
    assert client.get(path).status_code == 404
    assert client.get(path + "/menu").status_code == 404


def test_overlapping_restaurant_creates_keep_all_records(files):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: RestaurantRepository(files[0]).create(RESTAURANT), range(20)))
    assert len({row["id"] for row in results}) == 20
    assert len(RestaurantRepository(files[0]).get_all()) == 20


def test_import_and_static_serving_from_another_directory(tmp_path):
    import os
    result = subprocess.run(
        [sys.executable, "-c", "from app.main import app; from fastapi.testclient import TestClient; assert TestClient(app).get('/').status_code == 200"],
        cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])},
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr


def test_concurrent_delete_and_menu_add_preserve_ownership(files):
    from concurrent.futures import ThreadPoolExecutor
    from app.schema.menu_schema import MenuItemCreate
    from app.schema.restaurant_schema import CreateRestaurant

    restaurants = RestaurantRepository(files[0])
    menus = MenuRepository(files[1])
    restaurant_service = RestaurantService(restaurants, menus)
    menu_service = MenuService(menus, restaurants)
    rid = restaurant_service.create_restaurant(CreateRestaurant(**RESTAURANT)).id

    def add():
        try:
            menu_service.add_item(rid, MenuItemCreate(**ITEM))
        except LookupError:
            pass  # Deletion won; adding to the missing restaurant must fail.

    def delete():
        try:
            restaurant_service.delete_restaurant(rid)
        except ValueError:
            pass  # Adding won; deletion must retain the restaurant.

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(add), pool.submit(delete)]
        for future in futures:
            future.result(timeout=5)
    assert not menus.get_by_restaurant(rid) or restaurants.get_by_id(rid) is not None
