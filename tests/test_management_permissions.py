import json

import pytest
from fastapi.testclient import TestClient

from app.api import dependencies
from app.api.routers import menu_routers, restaurant_routers
from app.main import app
from app.repository.menu_repo import MenuRepository
from app.repository.restaurant_repo import RestaurantRepository
from app.repository.users_repo import UserRepository
from app.schema.menu_schema import MenuItemCreate
from app.schema.restaurant_schema import UpdateRestaurant
from app.services.menu_service import MenuService
from app.services.restaurant_service import RestaurantService

RESTAURANT = {'name': 'Cafe', 'cuisine': 'Cafe', 'address': '1 St', 'is_open': True}
ITEM = {'name': 'Tea', 'description': 'Green tea', 'price': 3.10,
        'category': 'drinks', 'is_available': True}


@pytest.fixture
def management_data(tmp_path, monkeypatch):
    users = UserRepository(tmp_path / 'users.json')
    monkeypatch.setattr(dependencies.user_service, 'repository', users)
    monkeypatch.setattr(dependencies.user_service, '_sessions', {})
    restaurant_file = tmp_path / 'restaurants.json'
    menu_file = tmp_path / 'menu.json'
    restaurant_file.write_text(json.dumps([
        {**RESTAURANT, 'id': 1, 'owner_id': 2},
        {**RESTAURANT, 'id': 2, 'owner_id': 3},
        {**RESTAURANT, 'id': 3},
    ]))
    menu_file.write_text(json.dumps([{**ITEM, 'id': 1, 'restaurant_id': 1}]))
    restaurants = RestaurantService(RestaurantRepository(restaurant_file))
    menus = MenuService(MenuRepository(menu_file), restaurants.repository)
    monkeypatch.setattr(restaurant_routers, 'service', restaurants)
    monkeypatch.setattr(menu_routers, 'service', menus)
    try:
        with TestClient(app) as client:
            tokens = {}
            for role, email in [('customer', 'customer@example.ca'), ('owner', 'owner1@example.ca'),
                                ('owner', 'owner2@example.ca'), ('admin', 'admin@example.ca')]:
                created = client.post('/users', json={
                    'name': 'Test', 'last_name': 'User', 'email': email, 'password': 'secret123',
                })
                assert created.status_code == 201
                # Only trusted setup grants roles; public registration cannot do this.
                users.update(created.json()['id'], {'role': role})
                login = client.post('/auth/login', json={'email': email, 'password': 'secret123'})
                tokens[email] = {'Authorization': 'Bearer ' + login.json()['access_token']}
            yield client, tokens, restaurants, menus, users, restaurant_file, menu_file
    finally:
        app.dependency_overrides.clear()


def mutation_requests():
    return [
        ('POST', '/restaurants', RESTAURANT),
        ('PUT', '/restaurants/1', RESTAURANT),
        ('DELETE', '/restaurants/1', None),
        ('POST', '/restaurants/1/menu/items', ITEM),
        ('PUT', '/restaurants/1/menu/items/1', ITEM),
        ('DELETE', '/restaurants/1/menu/items/1', None),
        ('PUT', '/restaurants/1/owner', {'owner_id': 3}),
    ]


def test_anonymous_and_customer_cannot_change_management_data(management_data):
    client, tokens, restaurants, menus, users, restaurant_file, menu_file = management_data
    original_restaurants = restaurant_file.read_text()
    original_menu = menu_file.read_text()
    for method, path, body in mutation_requests():
        assert client.request(method, path, json=body).status_code == 401
        response = client.request(method, path, json=body, headers=tokens['customer@example.ca'])
        assert response.status_code == 403
    assert restaurant_file.read_text() == original_restaurants
    assert menu_file.read_text() == original_menu
    assert client.get('/restaurants').status_code == 200
    assert client.get('/restaurants/1/menu').status_code == 200


def test_owner_can_manage_own_restaurant_and_menu(management_data):
    client, tokens, restaurants, menus, users, restaurant_file, menu_file = management_data
    headers = tokens['owner1@example.ca']
    assert client.put('/restaurants/1', json={**RESTAURANT, 'name': 'Updated Cafe'}, headers=headers).status_code == 200
    added = client.post('/restaurants/1/menu/items', json=ITEM, headers=headers)
    assert added.status_code == 201
    item_id = added.json()['id']
    assert client.put(f'/restaurants/1/menu/items/{item_id}', json={**ITEM, 'price': 4.25}, headers=headers).status_code == 200
    assert client.delete(f'/restaurants/1/menu/items/{item_id}', headers=headers).status_code == 204
    created = client.post('/restaurants', json=RESTAURANT, headers=headers)
    assert created.status_code == 201
    assert created.json()['owner_id'] == 2
    saved = RestaurantRepository(restaurant_file).get_by_id(created.json()['id'])
    assert saved['owner_id'] == 2
    assert client.delete('/restaurants/' + str(created.json()['id']), headers=headers).status_code == 200


def test_owner_cannot_manage_another_or_unassigned_restaurant(management_data):
    client, tokens, restaurants, menus, users, restaurant_file, menu_file = management_data
    headers = tokens['owner2@example.ca']
    original_restaurants = restaurant_file.read_text()
    original_menu = menu_file.read_text()
    for method, path, body in mutation_requests()[1:]:
        assert client.request(method, path, json=body, headers=headers).status_code == 403
    assert client.put('/restaurants/3', json=RESTAURANT, headers=headers).status_code == 403
    assert restaurant_file.read_text() == original_restaurants
    assert menu_file.read_text() == original_menu


def test_admin_can_manage_all_and_assign_owner(management_data):
    client, tokens, restaurants, menus, users, restaurant_file, menu_file = management_data
    headers = tokens['admin@example.ca']
    assert client.put('/restaurants/1', json=RESTAURANT, headers=headers).status_code == 200
    assert client.post('/restaurants/2/menu/items', json=ITEM, headers=headers).status_code == 201
    assigned = client.put('/restaurants/3/owner', json={'owner_id': 3}, headers=headers)
    assert assigned.status_code == 200
    assert assigned.json()['owner_id'] == 3
    assert client.put('/restaurants/3', json=RESTAURANT, headers=tokens['owner2@example.ca']).status_code == 200
    assert RestaurantRepository(restaurant_file).get_by_id(3)['owner_id'] == 3
    removed = client.put('/restaurants/3/owner', json={'owner_id': None}, headers=headers)
    assert removed.status_code == 200
    assert client.put('/restaurants/3', json=RESTAURANT, headers=tokens['owner2@example.ca']).status_code == 403


def test_admin_cannot_assign_customer_or_inactive_owner(management_data):
    client, tokens, restaurants, menus, users, restaurant_file, menu_file = management_data
    headers = tokens['admin@example.ca']
    original = restaurant_file.read_text()
    assert client.put('/restaurants/1/owner', json={'owner_id': 1}, headers=headers).status_code == 409
    assert client.put('/restaurants/1/owner', json={'owner_id': 99}, headers=headers).status_code == 404
    users.update(3, {'is_active': False})
    assert client.put('/restaurants/1/owner', json={'owner_id': 3}, headers=headers).status_code == 403
    assert restaurant_file.read_text() == original


def test_inactive_manager_and_expired_token_rejected(management_data):
    client, tokens, restaurants, menus, users, restaurant_file, menu_file = management_data
    users.update(2, {'is_active': False})
    assert client.post('/restaurants/1/menu/items', json=ITEM, headers=tokens['owner1@example.ca']).status_code == 401
    assert client.delete('/restaurants/1', headers={'Authorization': 'Bearer invalid'}).status_code == 401


def test_ownership_and_role_cannot_be_changed_through_public_requests(management_data):
    client, tokens, restaurants, menus, users, restaurant_file, menu_file = management_data
    headers = tokens['owner1@example.ca']
    assert client.put('/restaurants/1', json={**RESTAURANT, 'owner_id': 3}, headers=headers).status_code == 422
    assert client.post('/restaurants', json={**RESTAURANT, 'owner_id': 3}, headers=headers).status_code == 422
    assert client.put('/users/me', json={'role': 'admin'}, headers=tokens['customer@example.ca']).status_code == 422
    assert client.post('/users', json={'name': 'Bad', 'last_name': 'User', 'email': 'bad@example.ca', 'password': 'secret123', 'role': 'admin'}).status_code == 422


def test_service_calls_also_enforce_management_access(management_data):
    client, tokens, restaurants, menus, users, restaurant_file, menu_file = management_data
    customer = dependencies.user_service.get_user(1)
    other_owner = dependencies.user_service.get_user(3)
    with pytest.raises(PermissionError):
        restaurants.update_restaurant(1, UpdateRestaurant(**RESTAURANT), customer)
    with pytest.raises(PermissionError):
        menus.add_item(1, MenuItemCreate(**ITEM), other_owner)
    with pytest.raises(PermissionError):
        menus.add_item(1, MenuItemCreate(**ITEM))
