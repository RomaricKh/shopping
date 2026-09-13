from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_product():
    response = client.get('/products/1')
    assert response.status_code == 200
    assert response.json() == {'id': 1, 'name': 'Product 1', 'price': 10.0}

def test_create_order():
    order = {'id': 1, 'products': [{'id': 1, 'name': 'Product 1', 'price': 10.0}], 'total': 10.0}
    response = client.post('/orders', json=order)
    assert response.status_code == 200
    assert response.json() == {'id': 1, 'products': [{'id': 1, 'name': 'Product 1', 'price': 10.0}], 'total': 10.0}