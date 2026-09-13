from fastapi import APIRouter, HTTPException
from models import Product, Order

router = APIRouter()

products = [
    Product(id=1, name='Laptop', price=1200.00, description='High-performance laptop'),
    Product(id=2, name='Smartphone', price=800.00, description='Latest smartphone model'),
]

orders = [
    Order(id=1, customer_id=1, products=[products[0]]),
    Order(id=2, customer_id=2, products=[products[1]]),
]

@router.get('/products', response_model=list[Product])
def get_products():
    return products

@router.get('/orders', response_model=list[Order])
def get_orders():
    return orders

@router.get('/products/{product_id}', response_model=Product)
def get_product(product_id: int):
    product = next((p for p in products if p.id == product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail='Product not found')
    return product

@router.post('/orders', response_model=Order)
def create_order(order: Order):
    orders.append(order)
    return order
