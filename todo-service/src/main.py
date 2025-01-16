from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.router import router
from src.middleware import AuthenticationMiddleware


app = FastAPI()

app.add_middleware(AuthenticationMiddleware)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
