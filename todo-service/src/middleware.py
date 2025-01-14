import jwt

from fastapi import Request, HTTPException

from src.main import app
from src.settings.config import settings


@app.middleware("http")
async def authentication_middleware(request: Request, call_next):
    token = request.headers.get("id-token")
    if not token:
        raise HTTPException(status_code=401, detail="Unathorized")
    
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
    setattr(request.state, "user", payload)
    return call_next(request)
