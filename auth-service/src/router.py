from fastapi import APIRouter

from src.db import SessionDependency
from src.service import AuthenticationService


router = APIRouter("/api/v1")

@router.get("/authenticate")
def authenticate(session: SessionDependency):
    auth_service = AuthenticationService(session)
    is_authenticated = auth_service.authenticate()
    return is_authenticated
