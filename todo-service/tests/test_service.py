import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, select, func, col

from tests.fixtures import client_fixture, session_fixture, clean_todo_table, three_todos_two_users


# Payload: {"id": 14, "email": "test@user.com"}
TEST_ID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdXNlci5jb20iLCJpZCI6MTR9.9V4u2hZ2IAgIBwQv5pLE-AOi0NGi9pSElAm3V-1ns7w"


def test_get_todos(three_todos_two_users, client: TestClient, session: Session):
    response = client.get("/api/v1/todo", headers={"id-token": TEST_ID_TOKEN})
    assert response.status_code == 200
    expected_response = [
        {
            "id": 1,
            "title": "Todo 1",
            "description": "Write test",
            "done": False,
            "user_id": 14,
        },
        {
            "id": 2,
            "title": "Todo 2",
            "description": "Run test",
            "done": False,
            "user_id": 14,
        }
    ]
    assert response.json() == expected_response


def test_get_todos_not_found(client: TestClient):
    response = client.get("/api/v1/todo", headers={"id-token": TEST_ID_TOKEN})
    assert response.status_code == 200
    assert response.json() == []


def test_get_todo(three_todos_two_users, client: TestClient):
    response = client.get("/api/v1/todo/1", headers={"id-token": TEST_ID_TOKEN})
    assert response.status_code == 200
    expected_response = {
        "id": 1,
        "title": "Todo 1",
        "description": "Write test",
        "done": False,
        "user_id": 14,
    }
    assert response.json() == expected_response


def test_get_todo_from_other_user(three_todos_two_users, client: TestClient):
    response = client.get("/api/v1/todo/3", headers={"id-token": TEST_ID_TOKEN})
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_create_todo(client: TestClient, session: Session):
    data = {
        "title": "Fix bug",
        "description": "Fix authentication bug",
    }
    response = client.post("/api/v1/todo", headers={"id-token": TEST_ID_TOKEN}, json=data)

    assert response.status_code == 201
    todo = response.json()
    assert todo["title"] == "Fix bug"
    assert todo["description"] == "Fix authentication bug"
    assert todo["user_id"] == 14
    assert isinstance(todo["done"], bool)
    assert not todo["done"]
    assert "id" in todo
    assert isinstance(todo["id"], int)
