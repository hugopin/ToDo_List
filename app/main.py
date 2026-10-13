from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, status

from app.database import (
    create_task,
    delete_task,
    get_task,
    init_database,
    list_tasks,
    update_task,
)
from app.schemas import TaskCreate, TaskResponse, TaskUpdate


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Prepara o banco antes de a aplicação receber requisições."""
    init_database()
    yield


app = FastAPI(title="ToDo List", lifespan=lifespan)


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(task: TaskCreate) -> dict:
    """Cria uma tarefa inicialmente pendente."""
    return create_task(task.title, task.description)


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks_endpoint(completed: bool | None = None) -> list[dict]:
    """Lista todas as tarefas ou filtra pela situação de conclusão."""
    return list_tasks(completed)


@app.get("/tasks/{id}", response_model=TaskResponse)
def get_task_endpoint(id: int) -> dict:
    """Consulta uma tarefa ou informa que ela não foi encontrada."""
    task = get_task(id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada.",
        )
    return task


@app.patch("/tasks/{id}", response_model=TaskResponse)
def update_task_endpoint(id: int, changes: TaskUpdate) -> dict:
    """Edita apenas os campos enviados de uma tarefa existente."""
    # Inclui somente os campos enviados, preservando os valores dos omitidos.
    task = update_task(id, changes.model_dump(exclude_unset=True))
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada.",
        )
    return task


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(id: int) -> Response:
    """Exclui uma tarefa ou informa que ela não foi encontrada."""
    if not delete_task(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
