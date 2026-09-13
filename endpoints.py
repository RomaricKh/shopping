from fastapi import APIRouter, HTTPException
from models import Product, Order

router = APIRouter()

PRODUCTS = {
    1: Product(id=1, name="Product 1", price=10.0),
    2: Product(id=2, name="Product 2", price=20.0)
}

@router.get('/products/{product_id}', response_model=Product)
async def get_product(product_id: int):
    if product_id in PRODUCTS:
        return PRODUCTS[product_id]
    raise HTTPException(status_code=404, detail="Product not found")

@router.post('/orders', response_model=Order)
async def create_order(order: Order):
    return order