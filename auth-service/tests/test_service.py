from fastapi.testclient import TestClient
from src.models import User
from tests.fixtures import single_test_user, client_fixture, session_fixture


def test_create_user(single_test_user, client: TestClient):
    response = client.post("/api/v1/authenticate", json={"email": "user@email.com", "password": "password"})
    assert response.status_code == 200
    assert response.json() == True
