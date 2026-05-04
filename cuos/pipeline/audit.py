from __future__ import annotations

import json
from pathlib import Path

from cuos.cognition.review_scheduler import build_review_tasks
from cuos.cognition.scoring import determine_understanding_level
from cuos.llm.prompt_registry import PromptRegistry
from cuos.schemas.audit import AuditResult
from cuos.schemas.cognition import SessionState, UnderstandingState
from cuos.storage.sqlite_store import SQLiteStore


def run_audit(paper_dir: Path, session_id: str, llm, prompt_dir: Path = Path("prompts"), db_path: Path | None = None) -> None:
    session = SessionState.model_validate_json((paper_dir / "sessions" / f"{session_id}.json").read_text(encoding="utf-8"))
    cognitive_dir = paper_dir / "cognitive"
    graph = json.loads((cognitive_dir / "candidate_graph.json").read_text(encoding="utf-8"))
    registry = PromptRegistry(prompt_dir)
    prompt_template = registry.load("answer_audit.md")

    results: list[tuple[str, AuditResult]] = []
    for turn in session.turns:
        prompt = prompt_template.replace("{{question}}", turn.question).replace("{{user_answer}}", turn.answer)
        prompt = prompt.replace("{{related_source_blocks}}", json.dumps(turn.related_source_blocks, ensure_ascii=False))
        prompt = prompt.replace("{{candidate_graph_context}}", json.dumps(graph, ensure_ascii=False))
        result = llm.chat_json([{"role": "user", "content": prompt}], AuditResult)
        results.append((turn.state, result))

    levels = [determine_understanding_level(r) for _, r in results]
    final_level = max(levels) if levels else "L0"
    all_issues = [issue for _, result in results for issue in result.issues]
    understanding = UnderstandingState(paper_id=paper_dir.name, level=final_level, weak_points=all_issues, updated_from_session=session_id)
    (cognitive_dir / "understanding_state.json").write_text(understanding.model_dump_json(indent=2), encoding="utf-8")

    report_lines = ["# Audit Report", ""]
    follow_up_lines = ["# Follow-up Questions", ""]
    for state, result in results:
        report_lines.extend([
            f"## {state}",
            f"- accuracy: {result.accuracy_score}",
            f"- completeness: {result.completeness_score}",
            f"- depth: {result.depth_score}",
            f"- transfer: {result.transfer_score}",
            f"- suggested_level: {result.suggested_understanding_level}",
            f"- issues: {', '.join(result.issues)}",
            f"- missing_evidence: {', '.join(result.missing_evidence)}",
            f"- corrected_understanding: {result.corrected_understanding}",
            "",
        ])
        if result.follow_up_question:
            follow_up_lines.append(f"- [{state}] {result.follow_up_question}")
    (cognitive_dir / "audit_report.md").write_text("\n".join(report_lines), encoding="utf-8")
    (cognitive_dir / "follow_up_questions.md").write_text("\n".join(follow_up_lines), encoding="utf-8")

    (cognitive_dir / "review_tasks.json").write_text(
        json.dumps([task.model_dump() for task in build_review_tasks(paper_dir.name)], ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if db_path is not None:
        store = SQLiteStore(db_path)
        for task in build_review_tasks(paper_dir.name):
            store.add_review_task(task)
