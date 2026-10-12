import sqlite3
from contextlib import closing
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "tasks.db"


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão; quem a utiliza deve fechá-la ao terminar."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    """Cria a tabela de tarefas, caso ela ainda não exista."""
    with closing(get_connection()) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
                    description TEXT,
                    completed INTEGER NOT NULL DEFAULT 0
                        CHECK (completed IN (0, 1))
                )
                """
            )


def create_task(title: str, description: str | None) -> dict:
    """Salva uma tarefa pendente e retorna seus dados."""
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, description) VALUES (?, ?)",
                (title, description),
            )
            row = connection.execute(
                "SELECT id, title, description, completed FROM tasks WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
    return dict(row)


def list_tasks(completed: bool | None = None) -> list[dict]:
    """Lista as tarefas por identificador, com filtro opcional de conclusão."""
    query = "SELECT id, title, description, completed FROM tasks"
    parameters = ()
    if completed is not None:
        query += " WHERE completed = ?"
        parameters = (int(completed),)
    query += " ORDER BY id"

    with closing(get_connection()) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [dict(row) for row in rows]


def get_task(task_id: int) -> dict | None:
    """Busca uma tarefa pelo identificador; retorna None se não existir."""
    with closing(get_connection()) as connection:
        row = connection.execute(
            "SELECT id, title, description, completed FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def update_task(task_id: int, changes: dict) -> dict | None:
    """Altera os campos enviados e retorna a tarefa, se ela existir."""
    allowed_fields = ("title", "description", "completed")
    fields = [field for field in allowed_fields if field in changes]

    with closing(get_connection()) as connection:
        with connection:
            if fields:
                assignments = ", ".join(f"{field} = ?" for field in fields)
                values = [changes[field] for field in fields]
                connection.execute(
                    f"UPDATE tasks SET {assignments} WHERE id = ?",
                    (*values, task_id),
                )
            row = connection.execute(
                "SELECT id, title, description, completed FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
    return dict(row) if row is not None else None
