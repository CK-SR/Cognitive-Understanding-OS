from pathlib import Path

from cuos.schemas.audit import AuditResult
from cuos.schemas.cognition import UnderstandingState


def run_audit(paper_dir: Path, latest_answer: str, llm) -> None:
    cognitive_dir = paper_dir / "cognitive"
    payload = llm.generate_json("audit", "answer_audit.md", {"answer": latest_answer})
    result = AuditResult.model_validate(payload)
    (cognitive_dir / "audit_report.md").write_text(
        f"# Audit\naccuracy={result.accuracy_score}\nissues={'; '.join(result.issues)}\n",
        encoding="utf-8",
    )
    state = UnderstandingState(paper_id=paper_dir.name, level="L1", weak_points=result.issues)
    (cognitive_dir / "understanding_state.json").write_text(state.model_dump_json(indent=2), encoding="utf-8")
