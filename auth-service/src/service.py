import bcrypt
import jwt

from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.db import SessionDependency
from src.models import User
from src.schemas import AuthenticationRequest
from src.settings.config import settings


def _get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_password = hashed_password.decode('utf8')
    return string_password


def _verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password)


class AuthenticationService:
    def __init__(self, session: SessionDependency):
        self.session = session

    def authenticate(self, payload: AuthenticationRequest) -> bool:
        user = self._get_user_by_email(payload.email)
        if not _verify_password(payload.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid email or password")

        return self._encode_user({"email": user.email, "id": user.id})

    def _get_user_by_email(self, email: str):
        with self.session as session:
            try:
                statement = select(User).where(User.email == email)
                results = session.exec(statement)
                return results.one()
            except NoResultFound:
                raise HTTPException(status_code=400, detail="Invalid email or password")

    def create_user(self, payload: AuthenticationRequest) -> User:
        with self.session as session:
            try:
                user = User(email=payload.email, password=_get_password_hash(payload.password))
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
            except IntegrityError:
                raise HTTPException(status_code=400, detail="Email already taken")

    def verify_token(self, token: str) -> bool:
        try:
            self._decode_user(token)
            return True
        except jwt.exceptions.DecodeError:
            return False

    def _encode_user(self, data: dict):
        return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")

    def _decode_user(self, token: str):
        return jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
