from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.db import SessionDependency
from src.models import Todo
from src.settings.config import settings


class TodoService:
    def __init__(self, session: SessionDependency):
        self.session = session

    def list(self, payload) -> []:
        return []
