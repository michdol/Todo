import bcrypt

from fastapi import HTTPException

from src.db import SessionDependency
from src.models import User
from src.schemas import AuthenticationRequest


def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_password = hashed_password.decode('utf8')
    return string_password


def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password)



class AuthenticationService:
    def __init__(self, session: SessionDependency):
        self.session = session

    def authenticate(self, payload: AuthenticationRequest) -> bool:
        user: User = self.session.get(User).where(email=payload.email)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid email or password")

        password_valid = verify_password(payload.password, user.password)
        if not password_valid:
            raise HTTPException(status_code=400, detail="Invalid email or password")

        # TODO: cookie
        return password_valid

    def create_user(self, payload: AuthenticationRequest) -> User:
        user = User(**payload.model_dump())
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
