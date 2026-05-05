from __future__ import annotations

import json
from pathlib import Path

from cuos.cognition.review_scheduler import build_review_tasks
from cuos.cognition.scoring import determine_understanding_level, max_level
from cuos.llm.prompt_registry import PromptRegistry
from cuos.schemas.audit import AuditResult
from cuos.schemas.cognition import SessionState, UnderstandingState
from cuos.schemas.graph import CognitiveGraph
from cuos.storage.sqlite_store import SQLiteStore


def run_audit(
    paper_dir: Path,
    session_id: str,
    llm,
    prompt_dir: Path = Path("prompts"),
    db_path: Path | None = None,
) -> None:
    session_path = paper_dir / "sessions" / f"{session_id}.json"
    if not session_path.exists():
        raise FileNotFoundError(
            f"Session file not found: {session_path}. Run 'cuos session' first."
        )
    session = SessionState.model_validate_json(session_path.read_text(encoding="utf-8"))
    cognitive_dir = paper_dir / "cognitive"
    candidate_graph_path = cognitive_dir / "candidate_graph.json"
    if not candidate_graph_path.exists():
        raise FileNotFoundError(
            f"candidate_graph.json not found in {cognitive_dir}. Run 'cuos map' first."
        )
    graph = CognitiveGraph.model_validate_json(candidate_graph_path.read_text(encoding="utf-8"))
    registry = PromptRegistry(prompt_dir)
    prompt_template = registry.load("answer_audit.md")

    results: list[tuple[str, AuditResult]] = []
    node_levels: dict[str, str] = {node.node_id: node.understanding_level for node in graph.nodes}
    node_weak_points: dict[str, list[str]] = {}

    for turn in session.turns:
        prompt = prompt_template.replace("{{question}}", turn.question).replace(
            "{{user_answer}}", turn.answer
        )
        prompt = prompt.replace(
            "{{related_source_blocks}}",
            json.dumps(turn.related_source_blocks, ensure_ascii=False),
        )
        prompt = prompt.replace(
            "{{candidate_graph_context}}",
            graph.model_dump_json(),
        )
        result = llm.chat_json([{"role": "user", "content": prompt}], AuditResult)
        results.append((turn.state, result))

        level = determine_understanding_level(result)
        for node_id in turn.related_node_ids:
            node_levels[node_id] = max_level(node_levels.get(node_id, "L0"), level)
            if result.issues:
                node_weak_points.setdefault(node_id, [])
                node_weak_points[node_id] = sorted(
                    set(node_weak_points[node_id] + result.issues)
                )

    # Persist node-level understanding back into the candidate graph.
    for node in graph.nodes:
        if node.node_id in node_levels:
            node.understanding_level = node_levels[node.node_id]
    candidate_graph_path.write_text(graph.model_dump_json(indent=2), encoding="utf-8")

    levels = [determine_understanding_level(result) for _, result in results]
    final_level = max_level(*levels) if levels else "L0"
    all_issues = [issue for _, result in results for issue in result.issues]
    weak_nodes = sorted(node_id for node_id, issues in node_weak_points.items() if issues)
    understanding = UnderstandingState(
        paper_id=paper_dir.name,
        level=final_level,
        weak_points=all_issues,
        updated_from_session=session_id,
        node_levels=node_levels,
        weak_nodes=weak_nodes,
        node_weak_points=node_weak_points,
    )
    (cognitive_dir / "understanding_state.json").write_text(
        understanding.model_dump_json(indent=2), encoding="utf-8"
    )

    report_lines = ["# Audit Report", ""]
    follow_up_lines = ["# Follow-up Questions", ""]
    for state, result in results:
        report_lines.extend(
            [
                f"## {state}",
                f"- accuracy: {result.accuracy_score}",
                f"- completeness: {result.completeness_score}",
                f"- depth: {result.depth_score}",
                f"- transfer: {result.transfer_score}",
                f"- suggested_level: {result.suggested_understanding_level}",
                f"- computed_level: {determine_understanding_level(result)}",
                f"- issues: {', '.join(result.issues)}",
                f"- missing_evidence: {', '.join(result.missing_evidence)}",
                f"- corrected_understanding: {result.corrected_understanding}",
                "",
            ]
        )
        if result.follow_up_question:
            follow_up_lines.append(f"- [{state}] {result.follow_up_question}")
    report_lines.extend(["## Node-level understanding", ""])
    for node_id, level in sorted(node_levels.items()):
        if level != "L0":
            report_lines.append(f"- {node_id}: {level}")
    (cognitive_dir / "audit_report.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )
    (cognitive_dir / "follow_up_questions.md").write_text(
        "\n".join(follow_up_lines), encoding="utf-8"
    )

    review_tasks = build_review_tasks(paper_dir.name)
    (cognitive_dir / "review_tasks.json").write_text(
        json.dumps(
            [task.model_dump() for task in review_tasks],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    if db_path is not None:
        store = SQLiteStore(db_path)
        for task in review_tasks:
            store.add_review_task(task)
