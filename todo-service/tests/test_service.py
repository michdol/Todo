import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.models import Todo
from tests.fixtures import client_fixture, session_fixture, clean_todo_table, three_todos_two_users


# Payload: {"id": 14, "email": "test@user.com"}
TEST_ID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAdXNlci5jb20iLCJpZCI6MTR9.9V4u2hZ2IAgIBwQv5pLE-AOi0NGi9pSElAm3V-1ns7w"

BASE_URL = "/api/v1/todo"

params = (
    ["GET", f"{BASE_URL}/todo"],
    ["GET", f"{BASE_URL}/todo/1"],
    ["POST", f"{BASE_URL}/todo"],
    ["PATCH", f"{BASE_URL}/todo/1"],
    ["DELETE", f"{BASE_URL}/todo/1"],
)

@pytest.mark.parametrize("method,endpoint", params)
def test_get_todos_no_id_token(three_todos_two_users, client: TestClient, session: Session, method: str, endpoint: str):
    response = client.request(method=method, url=endpoint)
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_get_todos(three_todos_two_users, client: TestClient, session: Session):
    response = client.get(f"{BASE_URL}/todo", headers={"id-token": TEST_ID_TOKEN})
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
    response = client.get(f"{BASE_URL}/todo", headers={"id-token": TEST_ID_TOKEN})
    assert response.status_code == 200
    assert response.json() == []


def test_get_todo(three_todos_two_users, client: TestClient):
    response = client.get(f"{BASE_URL}/todo/1", headers={"id-token": TEST_ID_TOKEN})
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
    response = client.get(f"{BASE_URL}/todo/3", headers={"id-token": TEST_ID_TOKEN})
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_create_todo(client: TestClient, session: Session):
    data = {
        "title": "Fix bug",
        "description": "Fix authentication bug",
    }
    response = client.post(f"{BASE_URL}/todo", headers={"id-token": TEST_ID_TOKEN}, json=data)

    assert response.status_code == 201
    todo = response.json()
    assert todo["title"] == "Fix bug"
    assert todo["description"] == "Fix authentication bug"
    assert todo["user_id"] == 14
    assert isinstance(todo["done"], bool)
    assert not todo["done"]
    assert "id" in todo
    assert isinstance(todo["id"], int)

    # Check DB
    todo_id = todo["id"]
    todo = session.get(Todo, todo_id)
    assert todo.title == "Fix bug"
    assert todo.description == "Fix authentication bug"
    assert todo.user_id == 14
    assert not todo.done
    assert todo.id == todo_id


def test_update_todo(three_todos_two_users, client: TestClient, session: Session):
    data = {
        "title": "Updated title",
        "done": True
    }
    response = client.patch(f"{BASE_URL}/todo/1", headers={"id-token": TEST_ID_TOKEN}, json=data)

    assert response.status_code == 200
    todo = response.json()
    assert todo["title"] == "Updated title"
    assert todo["description"] == "Write test"
    assert todo["user_id"] == 14
    assert todo["done"]
    assert todo["id"] == 1

    # Check from DB
    todo = session.get(Todo, 1)
    assert todo.title == "Updated title"
    assert todo.description == "Write test"
    assert todo.user_id == 14
    assert todo.done
    assert todo.id == 1


def test_update_todo_done_only(three_todos_two_users, client: TestClient, session: Session):
    data = {
        "done": True
    }
    response = client.patch(f"{BASE_URL}/todo/1", headers={"id-token": TEST_ID_TOKEN}, json=data)

    assert response.status_code == 200
    todo = response.json()
    assert todo["title"] == "Todo 1"
    assert todo["description"] == "Write test"
    assert todo["user_id"] == 14
    assert todo["done"]
    assert todo["id"] == 1

    # Check from DB
    todo = session.get(Todo, 1)
    assert todo.title == "Todo 1"
    assert todo.description == "Write test"
    assert todo.user_id == 14
    assert todo.done
    assert todo.id == 1


def test_delete_todo(three_todos_two_users, client: TestClient, session: Session):
    response = client.delete(f"{BASE_URL}/todo/1", headers={"id-token": TEST_ID_TOKEN})

    assert response.status_code == 204
    with session:
        statement = select(Todo).where(Todo.id == 1)
        results = session.exec(statement)
        assert results.first() is None
