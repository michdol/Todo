from fastapi import FastAPI

from src.router import router
from src.middleware import AuthenticationMiddleware


app = FastAPI()

app.add_middleware(AuthenticationMiddleware)

app.include_router(router)
