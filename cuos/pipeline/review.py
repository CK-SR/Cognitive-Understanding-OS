from __future__ import annotations

from datetime import date
from pathlib import Path

from cuos.cognition.scoring import determine_understanding_level, max_level
from cuos.llm.prompt_registry import PromptRegistry
from cuos.schemas.audit import AuditResult
from cuos.schemas.cognition import UnderstandingState
from cuos.storage.sqlite_store import SQLiteStore


def run_review(
    workspace_dir: Path,
    store: SQLiteStore,
    llm,
    prompt_dir: Path,
    paper_id: str | None = None,
    non_interactive_demo: bool = False,
) -> list[str]:
    tasks = store.list_due_tasks(date.today().isoformat(), paper_id=paper_id)
    registry = PromptRegistry(prompt_dir)
    prompt_template = registry.load("answer_audit.md")
    completed: list[str] = []

    for task in tasks:
        print(f"\n[{task.paper_id}] {task.question}")
        if non_interactive_demo:
            answer = "这是用于 smoke test 的演示回答。"
        else:
            print("请输入回答（空行结束）：")
            lines: list[str] = []
            while True:
                line = input()
                if line == "":
                    break
                lines.append(line)
            answer = "\n".join(lines).strip()

        paper_cognitive = workspace_dir / "papers" / task.paper_id / "cognitive"
        graph_context = _read_optional_text(paper_cognitive / "candidate_graph.json", "{}")
        state_path = paper_cognitive / "understanding_state.json"

        prompt = prompt_template.replace("{{question}}", task.question).replace(
            "{{user_answer}}", answer
        )
        prompt = prompt.replace("{{related_source_blocks}}", "[]").replace(
            "{{candidate_graph_context}}", graph_context
        )
        result = llm.chat_json([{"role": "user", "content": prompt}], AuditResult)

        prior = UnderstandingState(paper_id=task.paper_id, level="L0", weak_points=[])
        if state_path.exists():
            prior = UnderstandingState.model_validate_json(
                state_path.read_text(encoding="utf-8")
            )
        merged_issues = sorted(set(prior.weak_points + result.issues))
        new_state = UnderstandingState(
            paper_id=task.paper_id,
            level=max_level(prior.level, determine_understanding_level(result)),
            weak_points=merged_issues,
            updated_from_session=prior.updated_from_session,
            node_levels=prior.node_levels,
            weak_nodes=prior.weak_nodes,
            node_weak_points=prior.node_weak_points,
        )
        state_path.write_text(new_state.model_dump_json(indent=2), encoding="utf-8")

        store.update_review_task_status(task.task_id, "done")
        completed.append(task.task_id)

    return completed


def _read_optional_text(path: Path, default: str) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return default
