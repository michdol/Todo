from pydantic import BaseModel


class CreateTodoRequest(BaseModel):
    title: str
    description: str | None = ""
    done: bool | None = False
