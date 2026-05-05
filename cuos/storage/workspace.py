import sqlite3
from pathlib import Path


def init_workspace(workspace_dir: Path) -> None:
    workspace_dir.mkdir(parents=True, exist_ok=True)
    (workspace_dir / "papers").mkdir(exist_ok=True)
    (workspace_dir / "sessions").mkdir(exist_ok=True)
    (workspace_dir / "cognitive").mkdir(exist_ok=True)
    conn = sqlite3.connect(workspace_dir / "cuos.db")
    conn.execute(
        "create table if not exists review_tasks (task_id text, paper_id text, question text, due_date text, status text)"
    )
    conn.commit()
    conn.close()
