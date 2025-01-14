from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    description: str | None = Field()
    done: bool = Field(default=False, nullable=False)
    user_id: int = Field(allow_mutation=False, index=True)
