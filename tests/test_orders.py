from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_orders():
    response = client.get("/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_get_products():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 2

def test_get_nonexistent_product():
    response = client.get("/products/999")
    assert response.status_code == 404