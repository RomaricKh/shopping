from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_nonexistent_product():
    response = client.get("/products/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

def test_get_product_invalid_id_type():
    response = client.get("/products/invalid-id")
    assert response.status_code == 422

def test_create_order_invalid_payload():
    response = client.post("/orders", json={"invalid": "payload"})
    assert response.status_code == 422

def test_create_order_empty_payload():
    response = client.post("/orders", json={})
    assert response.status_code == 422

def test_create_order_valid():
    new_order = {
        "id": 99,
        "customer_id": 10,
        "products": [
            {"id": 1, "name": "Laptop", "price": 1200.0, "description": "High-performance laptop"}
        ]
    }
    response = client.post("/orders", json=new_order)
    assert response.status_code == 200
    assert response.json()["id"] == 99
    assert len(response.json()["products"]) == 1

def test_get_products_list():
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_get_orders_list():
    response = client.get("/orders")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

def test_delete_order_unsupported_method():
    response = client.delete("/orders")
    assert response.status_code == 405
