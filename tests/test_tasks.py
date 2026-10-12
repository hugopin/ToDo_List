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
