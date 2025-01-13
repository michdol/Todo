from typing import Annotated
from fastapi import APIRouter, Depends

from src.schemas import AuthenticationRequest, TokenRequest
from src.service import AuthenticationService


router = APIRouter(prefix="/api/v1")

authentication_service = Annotated[AuthenticationService, Depends(AuthenticationService)]


@router.post("/authenticate")
def authenticate(payload: AuthenticationRequest, service: authentication_service):
    is_authenticated = service.authenticate(payload)
    return is_authenticated


@router.post("/register")
def register(payload: AuthenticationRequest, service: authentication_service):
    service.create_user(payload)
    return True


@router.post("/verify_token")
def verify_token(payload: TokenRequest, service: authentication_service):
    # TODO: security this endpoint with API_KEY
    is_valid = service.verify_token(payload.token)
    return {"valid": is_valid}
