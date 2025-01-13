from fastapi import APIRouter

from src.db import SessionDependency
from src.schemas import AuthenticationRequest
from src.service import AuthenticationService


router = APIRouter(prefix="/api/v1")

@router.post("/authenticate")
def authenticate(session: SessionDependency, payload: AuthenticationRequest):
    auth_service = AuthenticationService(session)
    is_authenticated = auth_service.authenticate(payload)
    return is_authenticated
