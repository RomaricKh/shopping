from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    price: float

class Order(BaseModel):
    id: int
    products: list[Product]
    total: float