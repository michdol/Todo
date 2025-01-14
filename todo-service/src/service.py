from fastapi import HTTPException
from typing import Sequence
from sqlmodel import select
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.db import SessionDependency
from src.models import Todo
from src.schemas import CreateTodoRequest
from src.settings.config import settings


class TodoService:
    def __init__(self, session: SessionDependency):
        self.session = session

    def list(self, user_id: int) -> Sequence[Todo]:
        with self.session:
            statement = select(Todo).where(Todo.user_id == user_id)
            results = self.session.exec(statement)
            return results.all()

    def get(self, id_: int, user_id: int) -> Todo:
        with self.session:
            try:
                statement = select(Todo).where(Todo.user_id == user_id, Todo.id == id_)
                results = self.session.exec(statement)
                return results.one()
            except NoResultFound:
                raise HTTPException(404, detail="Not Found")

    def create(self, payload: CreateTodoRequest, user_id: int) -> Todo:
        with self.session:
            try:
                todo = Todo(**payload.model_dump(), user_id=user_id)
                self.session.add(todo)
                self.session.commit()
                self.session.refresh(todo)
                return todo
            except IntegrityError:
                raise HTTPException(400, detail="Bad Request")
