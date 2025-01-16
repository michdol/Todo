from fastapi import Depends
from typing import Annotated
from sqlmodel import Session, create_engine

from src.settings.config import settings


engine = create_engine(settings.DATABASE_URI)


def get_session():
    with Session(engine) as session:
        yield session


SessionDependency = Annotated[Session, Depends(get_session)]
