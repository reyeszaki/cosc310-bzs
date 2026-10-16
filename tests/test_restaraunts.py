from fastapi.testclient import TestClient
from app.main import app
import json
from app.repository.restaurant_repo import RestaurantRepository
from app.services.restaurant_service import RestaurantService

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_restaurants():
    response = client.get("/restaurants")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 2
    restaurant = data[0]
    assert "id" in restaurant
    assert "name" in restaurant
    assert "cuisine" in restaurant
    assert "address" in restaurant  
    assert "is_open" in restaurant  

def test_repository_with_isolated_data(tmp_path):
    test_file = tmp_path / "test_restaurants.json"
    fake_data = [
        {"id": 99, "name": "Fake Burger", "cuisine": "American", "address": "123 Fake St", "is_open": True}
    ]
    test_file.write_text(json.dumps(fake_data))
    repo = RestaurantRepository(data_path=str(test_file))
    result = repo.get_all()
    assert len(result) == 1
    assert result[0]["name"] == "Fake Burger"

def test_invalid_endpoint_failure_case():
    response = client.get("/api/nonexistent-restaurant-route")
    assert response.status_code == 404

def test_delete_restauraunt_invalid_id():
    response = client.delete("/restaurants/99")
    assert response.status_code == 404

def test_update_restaurant_invalid_data_type():
    response = client.put(
        "/restaurants/99",
    json={
        "name": "Fake Burger",
        "cuisine": "Russian",
        "address": "123 Fake St",
        "is_open": "yoyorue"

     },
    )
    assert response.status_code == 422

def test_create_restaurant_invalid_data():
    response = client.post(
        "/restaurants",
        json={
            "name": 45,
            "cuisine": "AMERICAN",
            "address": "123 Fake St",
            "is_open": True
        },
     )
    assert response.status_code == 422
SEARCH_SEED = [
    {"id": 1, "name": "Pizza Place", "cuisine": "Italian", "address": "456 Pizza Ave", "is_open": True},
    {"id": 2, "name": "Burger King", "cuisine": "American", "address": "1 Pizza St", "is_open": False},
    {"id": 3, "name": "Luigi's", "cuisine": "Italian", "address": "9 Main St", "is_open": False},
]


def make_search_service(tmp_path):
    test_file = tmp_path / "test_restaurants.json"
    test_file.write_text(json.dumps(SEARCH_SEED))
    repo = RestaurantRepository(data_path=test_file)
    return RestaurantService(repo)


def ids(restaurants):
    return [r.id for r in restaurants]


def test_restaurant_search(tmp_path):
    results = make_search_service(tmp_path).search_restaurants("pizza")
    assert ids(results) == [1]


def test_search_no_match(tmp_path):
    assert make_search_service(tmp_path).search_restaurants("sushi") == []


def test_search_blank_returns_all(tmp_path):
    assert len(make_search_service(tmp_path).search_restaurants("   ")) == 3


def test_search_no_argument_returns_all(tmp_path):
    assert len(make_search_service(tmp_path).search_restaurants()) == 3


def test_filter_by_cuisine(tmp_path):
    results = make_search_service(tmp_path).search_restaurants(cuisine="italian")
    assert ids(results) == [1, 3]


def test_filter_by_is_open_false(tmp_path):
    results = make_search_service(tmp_path).search_restaurants(is_open=False)
    assert ids(results) == [2, 3]


def test_search_and_cuisine_combined(tmp_path):
    results = make_search_service(tmp_path).search_restaurants(search="pizza", cuisine="italian")
    assert ids(results) == [1]


def test_search_endpoint_filters_by_name():
    response = client.get("/restaurants?search=ramen")
    assert response.status_code == 200
    assert all("ramen" in item["name"].lower() for item in response.json())


def test_search_endpoint_no_match():
    response = client.get("/restaurants?search=zzzz")
    assert response.status_code == 200
    assert response.json() == []


def test_endpoint_rejects_invalid_is_open():
    response = client.get("/restaurants?is_open=maybe")
    assert response.status_code == 422
