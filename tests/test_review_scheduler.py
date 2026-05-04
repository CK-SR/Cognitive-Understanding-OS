from datetime import date

from cuos.cognition.review_scheduler import build_review_tasks


def test_review_scheduler_offsets() -> None:
    tasks = build_review_tasks("paper-x", start_date=date(2026, 5, 1))
    assert [t.due_date for t in tasks] == ["2026-05-02", "2026-05-04", "2026-05-08", "2026-05-15"]
