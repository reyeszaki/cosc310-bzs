from fastapi.testclient import TestClient
from app.main import app
import json
from app.repository.restaurant_repo import RestaurantRepository

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
