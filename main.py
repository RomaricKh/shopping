from fastapi import FastAPI
from endpoints import router

app = FastAPI()

app.include_router(router)

# Define your data models and endpoints here