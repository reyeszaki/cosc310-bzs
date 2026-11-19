import pytest
from fastapi.testclient import TestClient

from app.api import dependencies
from app.main import app
from app.repository.users_repo import UserRepository

client = TestClient(app)

NEW_USER = {"name": "Ana", "last_name": "Lee", "email": "Ana@Example.ca", "password": "secret123"}

# makes a fresh empty users file for every test so real data never changes
@pytest.fixture(autouse=True)
def isolated_users(tmp_path, monkeypatch):
    monkeypatch.setattr(dependencies.user_service.repository, "data_path", tmp_path / "users.json")
    monkeypatch.setattr(dependencies.user_service, "_sessions", {})

# signs up a user, logs in, and gives back the token
def register_and_login(email="Ana@Example.ca"):
    client.post("/users", json={**NEW_USER, "email": email})
    response = client.post("/auth/login", json={"email": email, "password": "secret123"})
    return response.json()["access_token"]

# checks users are still saved after a restart and ids keep counting up
def test_repo_ids_survive_restart(tmp_path):
    path = tmp_path / "users.json"
    first = UserRepository(path).create({"email": "a@b.ca"})
    restarted = UserRepository(path)
    assert restarted.get_by_id(first["id"])["email"] == "a@b.ca"
    assert restarted.create({"email": "c@d.ca"})["id"] == first["id"] + 1

# checks sign up, login, and that /users/me needs a token
def test_api_register_login_and_me():
    created = client.post("/users", json=NEW_USER)
    assert created.status_code == 201
    assert "password" not in created.json() and "password_hash" not in created.json()

    token = client.post("/auth/login", json={"email": NEW_USER["email"], "password": "secret123"}).json()["access_token"]
    assert client.get("/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    assert client.get("/users/me").status_code == 401

# checks a normal customer can't open the admin page
def test_api_customer_forbidden_on_admin_route():
    token = register_and_login()
    response = client.get("/users/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

# checks a customer can log in and then see restaurants and a menu
def test_flow_customer_logs_in_and_browses_menu():
    token = register_and_login()
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/users/me", headers=headers)
    restaurants = client.get("/restaurants")
    first_id = restaurants.json()[0]["id"]
    menu = client.get(f"/restaurants/{first_id}/menu")
    assert me.status_code == 200 and me.json()["role"] == "customer"
    assert restaurants.status_code == 200 and len(restaurants.json()) > 0
    assert menu.status_code == 200 and menu.json()["restaurant_id"] == first_id

# checks login still works if the email has different capitals
def test_regression_login_ignores_email_case():
    client.post("/users", json=NEW_USER)
    response = client.post("/auth/login", json={"email": "ana@EXAMPLE.CA", "password": "secret123"})
    assert response.status_code == 200