from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from cuos.schemas.cognition import ReviewTask


def build_review_tasks(paper_id: str, start_date: date | None = None) -> list[ReviewTask]:
    anchor = start_date or date.today()
    schedule = [
        (1, "中心问题复述：不看原文，复述本文要解决的核心问题与价值。"),
        (3, "证据链重建：给出结论→机制→证据块编号的完整链条。"),
        (7, "迁移应用：将论文机制迁移到你的项目，说明改造步骤。"),
        (14, "反驳和边界：指出失败场景、反例及可接受边界。"),
    ]
    tasks: list[ReviewTask] = []
    for days, question in schedule:
        tasks.append(
            ReviewTask(
                task_id=f"{paper_id}-{uuid4().hex[:8]}",
                paper_id=paper_id,
                question=question,
                due_date=(anchor + timedelta(days=days)).isoformat(),
            )
        )
    return tasks
