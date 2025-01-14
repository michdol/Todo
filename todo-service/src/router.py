from typing import Annotated
from fastapi import APIRouter, Depends, Request

# from src.schemas import SomeRequest
from src.service import TodoService


router = APIRouter(prefix="/api/v1")

todo_service = Annotated[TodoService, Depends(TodoService)]


@router.post("/todo")
def get_todos(request: Request, service: todo_service):
    return service.list(request.state.user["id"])
