import jwt

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from src.settings.config import settings


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        token = request.headers.get("id-token")
        if not token:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            setattr(request.state, "user", payload)
        except jwt.exceptions.DecodeError:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        
        response = await call_next(request)
        return response
