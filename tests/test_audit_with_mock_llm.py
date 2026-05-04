from pathlib import Path

from cuos.llm.mock_client import MockLLMClient
from cuos.parsers.mock_parser import MockParser
from cuos.pipeline.audit import run_audit
from cuos.pipeline.build_map import run_map
from cuos.pipeline.ingest import run_ingest
from cuos.schemas.cognition import SessionState, SessionTurn
from cuos.storage.workspace import init_workspace


def test_audit_with_mock_llm(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    sample = tmp_path / "sample.md"
    sample.write_text("# T\nA\nB", encoding="utf-8")
    parsed = run_ingest(sample, tmp_path / "papers", MockParser(), db_path=tmp_path / "cuos.db")
    paper_dir = tmp_path / "papers" / parsed.doc_id
    run_map(paper_dir, MockLLMClient(), Path("prompts"))
    (paper_dir / "sessions").mkdir(exist_ok=True)
    session_id = "session_test"
    session = SessionState(
        paper_id=parsed.doc_id,
        session_id=session_id,
        current_state="DONE",
        turns=[SessionTurn(state="CENTRAL_PROBLEM", question="Q", answer="A", related_source_blocks=[])],
    )
    (paper_dir / "sessions" / f"{session_id}.json").write_text(session.model_dump_json(indent=2), encoding="utf-8")
    run_audit(paper_dir, session_id, MockLLMClient(), prompt_dir=Path("prompts"), db_path=tmp_path / "cuos.db")
    assert (paper_dir / "cognitive" / "audit_report.md").exists()
    assert (paper_dir / "cognitive" / "understanding_state.json").exists()
