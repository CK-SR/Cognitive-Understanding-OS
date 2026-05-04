import sqlite3
from pathlib import Path

from cuos.schemas.cognition import ReviewTask


class SQLiteStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def add_review_task(self, task: ReviewTask) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "insert into review_tasks (task_id,paper_id,question,due_date,status) values (?,?,?,?,?)",
            (task.task_id, task.paper_id, task.question, task.due_date, task.status),
        )
        conn.commit()
        conn.close()

    def list_due_tasks(self, due_date: str) -> list[ReviewTask]:
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("select task_id,paper_id,question,due_date,status from review_tasks where due_date<=?", (due_date,)).fetchall()
        conn.close()
        return [ReviewTask(task_id=r[0], paper_id=r[1], question=r[2], due_date=r[3], status=r[4]) for r in rows]
