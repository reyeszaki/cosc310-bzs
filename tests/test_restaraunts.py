from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_restaurants():
    """Test that the restaurant endpoint returns a list with representative data matching the Pydantic schema."""
    response = client.get("/restaurants")
    assert response.status_code == 200
    data = response.json()
    
    # Verify it's a list containing at least 2 restaurants
    assert isinstance(data, list)
    assert len(data) >= 2
    
    # Check fields of the first restaurant (Pydantic contract check)
    restaurant = data[0]
    assert "id" in restaurant
    assert "name" in restaurant
    assert "cuisine" in restaurant
    assert "rating" in restaurant

def test_invalid_endpoint_failure_case():
    """Test a failure/invalid case (404 Not Found) as required for Milestone 0."""
    response = client.get("/api/nonexistent-restaurant-route")
    assert response.status_code == 404