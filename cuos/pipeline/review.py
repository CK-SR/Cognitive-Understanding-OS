from datetime import date

from cuos.storage.sqlite_store import SQLiteStore


def run_review(store: SQLiteStore) -> list[str]:
    tasks = store.list_due_tasks(date.today().isoformat())
    return [f"[{t.paper_id}] {t.question}" for t in tasks]
