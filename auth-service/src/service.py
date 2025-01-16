import bcrypt
import jwt

from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.db import SessionDependency
from src.models import User
from src.schemas import AuthenticationRequest
from src.settings.config import settings


def _get_password_hash(password) -> str:
    """
    Hashes plaintext password.

    Args:
        password: plaintext password

    Returns:
        cyphertext password
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_password = hashed_password.decode('utf8')
    return string_password


def _verify_password(plain_password, hashed_password) -> bool:
    """
    Checks if plaintext password matches cyphertext password.

    Args:
        plain_password: plaintext password
        hashed_password: cyphertext password

    Returns:
        True if password matches, False otherwise
    """
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password)


class AuthenticationService:
    """
    Service to register and authenticate users.
    """
    def __init__(self, session: SessionDependency):
        self.session = session

    def authenticate(self, payload: AuthenticationRequest) -> str:
        """
        Authenticates user by email and password.

        Args:
            payload: email and plaintext password

        Returns:
            JWT token

        Raises:
            HTTPException if user is not found or password doesn't match
        """
        try:
            user = self._get_user_by_email(payload.email)
        except NoResultFound:
            raise HTTPException(status_code=400, detail="Invalid email or password")

        if not _verify_password(payload.password, user.password):
            raise HTTPException(status_code=400, detail="Invalid email or password")

        return self._encode_user({"email": user.email, "id": user.id})

    def _get_user_by_email(self, email: str) -> User:
        """
        Retrieves User record by email.

        Args:
            email: user's email

        Returns:
            User record if found
        """
        with self.session as session:
            statement = select(User).where(User.email == email)
            results = session.exec(statement)
            return results.one()

    def create_user(self, payload: AuthenticationRequest) -> User:
        """
        Creates User record.

        Args:
            payload: email and password

        Returns:
            User record

        Raises:
            HTTPException if user with given email already exists
        """
        with self.session as session:
            try:
                user = User(email=payload.email, password=_get_password_hash(payload.password))
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
            except IntegrityError:
                raise HTTPException(status_code=400, detail="Email already taken")

    def _encode_user(self, data: dict) -> str:
        """
        Creates JWT token with given payload.

        Args:
            data: payload for JWT token

        Returns:
            generated token
        """
        return jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")

    def _decode_user(self, token: str) -> dict:
        """
        Decodes JWT token.

        Args:
            token: JWT token to decode

        Returns:
            JWT token's payload
        """
        return jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
