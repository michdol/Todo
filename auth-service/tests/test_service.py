import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, select, func, col

from src.models import User
from src.service import AuthenticationService
from tests.fixtures import single_test_user, client_fixture, session_fixture, clean_user_table


def test_authenticate_with_password(single_test_user, client: TestClient, session: Session):
    response = client.post("/api/v1/authenticate", json={"email": "user@email.com", "password": "password"})
    assert response.status_code == 200
    token = response.json()
    service = AuthenticationService(session)
    service._decode_user(token)


def test_authenticate_with_password_password_incorrect(single_test_user, client: TestClient, session: Session):
    response = client.post("/api/v1/authenticate", json={"email": "user@email.com", "password": "wrong-password"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email or password"}


def test_authenticate_with_password_email_incorrect(single_test_user, client: TestClient, session: Session):
    response = client.post("/api/v1/authenticate", json={"email": "wrong-user@email.com", "password": "password"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email or password"}


def test_register(client: TestClient, session: Session):
    response = client.post("/api/v1/register", json={"email": "user@email.com", "password": "password"})
    assert response.status_code == 200

    with session:
        statement = select(User).where(User.email == "user@email.com")
        result = session.exec(statement)
        user = result.one()
        assert user.email == "user@email.com"


def test_register_existing_email(single_test_user, client: TestClient, session: Session):
    response = client.post("/api/v1/register", json={"email": "user@email.com", "password": "password"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already taken"}

    with session:
        count = session.exec(select(func.count(col(User.id)))).one()
        assert count == 1


def test_register_invalid_email(client: TestClient, session: Session):
    response = client.post("/api/v1/register", json={"email": "user@email", "password": "password"})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"].startswith("value is not a valid email address")

    with session:
        count = session.exec(select(func.count(col(User.id)))).one()
        assert count == 0


def test_verify_token(client: TestClient, session: Session):
    service = AuthenticationService(session)
    user = User(email="user@email.com", password="password")
    token = service._encode_user(user)
    response = client.post("/api/v1/verify_token", json={"token": token})
    assert response.status_code == 200
    assert response.json() == {"valid": True}


def test_verify_token_invalid_token(client: TestClient, session: Session):
    token = "any string"
    response = client.post("/api/v1/verify_token", json={"token": token})
    assert response.status_code == 200
    assert response.json() == {"valid": False}
