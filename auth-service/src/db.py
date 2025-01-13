from fastapi import Depends
from typing import Annotated
from sqlmodel import Session, SQLModel, create_engine, select

from src.settings import Settings

engine = create_engine(Settings.DATABASE_URI)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]
