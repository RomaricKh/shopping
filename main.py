from fastapi import FastAPI
from endpoints import router

app = FastAPI(title="Shopping API")
app.include_router(router)