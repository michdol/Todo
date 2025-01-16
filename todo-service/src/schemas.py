from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional


class CreateTodoRequest(BaseModel):
    title: str
    description: str | None = ""
    done: bool | None = False


class PatchTodoRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None


@dataclass
class User:
    id: int
    email: str
