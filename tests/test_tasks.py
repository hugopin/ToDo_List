import pytest

from fastapi.testclient import TestClient

from app import database
from app.main import app


def test_create_task_starts_pending(tmp_path, monkeypatch):
    """Uma tarefa criada recebe identificador e começa pendente."""
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "tasks.db")

    with TestClient(app) as client:
        response = client.post(
            "/tasks",
            json={
                "title": "Estudar FastAPI",
                "description": "Acompanhar o miniprojeto da UFG",
            },
        )

    assert response.status_code == 201
    task = response.json()
    assert isinstance(task["id"], int)
    assert task["id"] > 0
    assert task["title"] == "Estudar FastAPI"
    assert task["description"] == "Acompanhar o miniprojeto da UFG"
    assert task["completed"] is False


@pytest.mark.parametrize("title", ["", "   "])
def test_create_task_rejects_blank_title(title, tmp_path, monkeypatch):
    """Títulos vazios são rejeitados sem salvar uma tarefa."""
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "tasks.db")

    with TestClient(app) as client:
        response = client.post("/tasks", json={"title": title})

        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any(error["loc"] == ["body", "title"] for error in errors)

        listing = client.get("/tasks")
        assert listing.status_code == 200
        assert listing.json() == []


def test_get_nonexistent_task_returns_404(tmp_path, monkeypatch):
    """Consultar um identificador inexistente retorna um erro claro."""
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "tasks.db")

    with TestClient(app) as client:
        response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Tarefa não encontrada."}


def test_update_title_preserves_omitted_fields(tmp_path, monkeypatch):
    """Editar somente o título preserva os outros campos e salva a alteração."""
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "tasks.db")

    with TestClient(app) as client:
        created = client.post(
            "/tasks",
            json={"title": "Estudar FastAPI", "description": "Descrição original"},
        )
        assert created.status_code == 201
        task_id = created.json()["id"]

        completed = client.patch(f"/tasks/{task_id}", json={"completed": True})
        assert completed.status_code == 200
        original = completed.json()
        assert original["completed"] is True

        response = client.patch(
            f"/tasks/{task_id}", json={"title": "Revisar FastAPI"}
        )
        expected = {**original, "title": "Revisar FastAPI"}
        assert response.status_code == 200
        assert response.json() == expected

        saved = client.get(f"/tasks/{task_id}")
        assert saved.status_code == 200
        assert saved.json() == expected


def test_delete_task_returns_204_and_removes_task(tmp_path, monkeypatch):
    """Excluir uma tarefa retorna uma resposta vazia e impede nova consulta."""
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "tasks.db")

    with TestClient(app) as client:
        created = client.post("/tasks", json={"title": "Teste de exclusão"})
        assert created.status_code == 201
        task_id = created.json()["id"]

        deleted = client.delete(f"/tasks/{task_id}")
        assert deleted.status_code == 204
        assert deleted.content == b""

        missing = client.get(f"/tasks/{task_id}")
        assert missing.status_code == 404
        assert missing.json() == {"detail": "Tarefa não encontrada."}

        repeated = client.delete(f"/tasks/{task_id}")
        assert repeated.status_code == 404
        assert repeated.json() == {"detail": "Tarefa não encontrada."}


def test_list_tasks_filters_by_completion(tmp_path, monkeypatch):
    """A listagem retorna todas as tarefas ou somente a situação solicitada."""
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "tasks.db")

    with TestClient(app) as client:
        pending = client.post("/tasks", json={"title": "Tarefa pendente"})
        assert pending.status_code == 201
        pending_task = pending.json()

        created = client.post("/tasks", json={"title": "Tarefa concluída"})
        assert created.status_code == 201
        completed = client.patch(
            f"/tasks/{created.json()['id']}", json={"completed": True}
        )
        assert completed.status_code == 200
        completed_task = completed.json()
        assert completed_task["completed"] is True

        all_tasks = client.get("/tasks")
        assert all_tasks.status_code == 200
        assert all_tasks.json() == [pending_task, completed_task]

        pending_tasks = client.get("/tasks", params={"completed": "false"})
        assert pending_tasks.status_code == 200
        assert pending_tasks.json() == [pending_task]

        completed_tasks = client.get("/tasks", params={"completed": "true"})
        assert completed_tasks.status_code == 200
        assert completed_tasks.json() == [completed_task]
