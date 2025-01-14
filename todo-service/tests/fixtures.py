import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, delete
from sqlmodel.pool import StaticPool

from src.db import get_session
from src.main import app
from src.models import Todo
from src.settings.config import settings


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(settings.DATABASE_URI, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_todo_table(session: Session):
    with session:
        statement = delete(Todo)
        session.exec(statement)
        session.commit()
    yield
    with session:
        statement = delete(Todo)
        session.exec(statement)
        session.commit()


@pytest.fixture
def three_todos_two_users(session: Session):
    todo_1 = Todo(id=1, title="Todo 1", description="Write test", user_id=14)
    todo_2 = Todo(id=2, title="Todo 2", description="Run test", user_id=14)
    todo_3 = Todo(id=3, title="Todo 3", description="Debug", user_id=2)
    session.add(todo_1)
    session.add(todo_2)
    session.add(todo_3)
    session.commit()
    yield
