from fastapi import FastAPI
from endpoints import app as shopping_app

app = FastAPI()
app.mount('/shopping', shopping_app)
