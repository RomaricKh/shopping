from fastapi import FastAPI, HTTPException
from models import Product, Order

app = FastAPI()

# Mock data
products = [
    Product(id=1, name='Laptop', price=1200.00, description='High-performance laptop'),
    Product(id=2, name='Smartphone', price=800.00, description='Latest smartphone model'),
]

orders = [
    Order(id=1, customer_id=1, products=[products[0]]),
    Order(id=2, customer_id=2, products=[products[1]]),
]

@app.get('/products', response_model=list[Product])
def get_products():
    return products

@app.get('/orders', response_model=list[Order])
def get_orders():
    return orders

@app.get('/products/{product_id}', response_model=Product)
def get_product(product_id: int):
    product = next((p for p in products if p.id == product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail='Product not found')
    return product

@app.get('/orders/{order_id}', response_model=Order)
def get_order(order_id: int):
    order = next((o for o in orders if o.id == order_id), None)
    if order is None:
        raise HTTPException(status_code=404, detail='Order not found')
    return order
