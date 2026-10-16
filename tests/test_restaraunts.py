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

def test_restaurant_search(tmp_path):
    test_file=tmp_path / "test_restaurants.json"
    repo= RestaurantRepository(data_path=str(tmp_path / "test_restaurants.json"))
    fake_data = [
        {"id": 1, "name": "Pizza Place", "cuisine": "Italian", "address": "456 Pizza Ave", "is_open": True},
        {"id": 2, "name": "Burger King", "cuisine": "American", "address": "789 Burger Blvd", "is_open": False}
    ]
    test_file.write_text(json.dumps(fake_data))
    service = RestaurantService(repo)
    results = service.search_restaurants("Pizza")
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0].name == "Pizza Place"
