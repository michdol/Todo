from fastapi import HTTPException
from typing import Sequence
from sqlmodel import select, update
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.db import SessionDependency
from src.models import Todo
from src.schemas import CreateTodoRequest, PatchTodoRequest


class TodoService:
    def __init__(self, session: SessionDependency):
        self.session = session

    def list(self, user_id: int) -> Sequence[Todo]:
        """
        Retrieves list of User's Todos.
        User can only see his own Todos.

        Args:
            user_id: user's id

        Returns:
            list of user's todos
        """
        with self.session:
            statement = select(Todo).where(Todo.user_id == user_id)
            results = self.session.exec(statement)
            return results.all()

    def get(self, id_: int, user_id: int) -> Todo:
        """
        Retrieves single Todo by its id and user's id.
        User can only see his own Todos.

        Args:
            id_: id of a Todo
            user_id: user's id

        Returns:
            Todo

        Raises:
            HTTPException: if a Todo is not found
        """
        with self.session:
            try:
                statement = select(Todo).where(Todo.user_id == user_id, Todo.id == id_)
                results = self.session.exec(statement)
                return results.one()
            except NoResultFound:
                raise HTTPException(404, detail="Not Found")

    def create(self, payload: CreateTodoRequest, user_id: int) -> Todo:
        """
        Creates a Todo.

        Args:
            payload: data to create a todo
            user_id: creator's id

        Returns:
            created Todo

        Raises:
            HTTPException if a database integrity error is raised
        """
        with self.session:
            try:
                todo = Todo(**payload.model_dump(), user_id=user_id)
                self.session.add(todo)
                self.session.commit()
                self.session.refresh(todo)
                return todo
            except IntegrityError:
                raise HTTPException(400, detail="Bad Request")

    def update(self, id_: int, payload: PatchTodoRequest, user_id: int) -> Todo:
        """
        Updates a Todo.

        Args:
            id_: taret Todo's id
            payload: data to update

        Returns:
            updated Todo
        """
        with self.session as session:
            todo = self.get(id_, user_id)
            update_data = payload.model_dump(exclude_unset=True)
            item = todo.model_copy(update=update_data)
            statement = update(Todo).where(Todo.id == todo.id).values(item.model_dump())
            session.exec(statement)
            session.commit()
            return self.get(id_, user_id)

    def delete(self, id_: int, user_id: int):
        """
        Deletes a Todo.
        User can delete only his own Todos.

        Args:
            id_: target Todo's id
            user_id: owner's id
        """
        todo = self.get(id_, user_id)
        with self.session:
            self.session.delete(todo)
            self.session.commit()
