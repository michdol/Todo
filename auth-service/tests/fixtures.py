import pytest

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, delete
from sqlmodel.pool import StaticPool

from src.db import get_session
from src.main import app
from src.models import User
from src.settings.config import settings
from src.service import _get_password_hash


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


@pytest.fixture
def single_test_user(session: Session):
    user = User(email="user@email.com", password=_get_password_hash("password"))
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user
    session.delete(user)
    session.commit()


@pytest.fixture(autouse=True)
def clean_user_table(session: Session):
    with session:
        statement = delete(User)
        session.exec(statement)
        session.commit()
