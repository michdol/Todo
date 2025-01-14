from typing import Annotated
from fastapi import APIRouter, Depends, Request

from src.schemas import CreateTodoRequest
from src.service import TodoService


router = APIRouter(prefix="/api/v1")

todo_service = Annotated[TodoService, Depends(TodoService)]


@router.get("/todo")
def get_todos(request: Request, service: todo_service):
    return service.list(user_id=request.state.user["id"])


@router.post("/todo", status_code=201)
def create_todo(payload: CreateTodoRequest, request: Request, service: todo_service):
    return service.create(payload, user_id=request.state.user["id"])


@router.get("/todo/{id_}")
def get_todo(id_: int, request: Request, service: todo_service):
    return service.get(id_, user_id=request.state.user["id"])
