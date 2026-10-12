from pydantic import BaseModel, field_validator


def validate_title(value: str) -> str:
    title = value.strip()
    if not title:
        raise ValueError("O título não pode estar vazio.")
    return title


class TaskCreate(BaseModel):
    """Dados necessários para criar uma tarefa."""

    title: str
    description: str | None = None

    @field_validator("title")
    @classmethod
    def check_title(cls, value: str) -> str:
        return validate_title(value)


class TaskUpdate(BaseModel):
    """Dados enviados para alterar apenas parte de uma tarefa."""

    title: str | None = None
    description: str | None = None
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def check_title(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("O título não pode ser nulo.")
        return validate_title(value)

    @field_validator("completed")
    @classmethod
    def check_completed(cls, value: bool | None) -> bool:
        if value is None:
            raise ValueError("A situação de conclusão não pode ser nula.")
        return value


class TaskResponse(BaseModel):
    """Dados de uma tarefa devolvidos pela API."""

    id: int
    title: str
    description: str | None
    completed: bool
