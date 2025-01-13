from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.db import create_db_and_tables
from src.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)
