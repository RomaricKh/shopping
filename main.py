from fastapi import FastAPI
from endpoints import router
from cli import cli

app = FastAPI()

app.include_router(router)

if __name__ == '__main__':
    cli()