from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str

class Order(BaseModel):
    id: int
    customer_id: int
    products: list[Product]
