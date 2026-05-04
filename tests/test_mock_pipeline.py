from pathlib import Path

from cuos.llm.mock_client import MockLLMClient
from cuos.parsers.mock_parser import MockParser
from cuos.pipeline.build_map import run_map
from cuos.pipeline.ingest import run_ingest
from cuos.storage.workspace import init_workspace


def test_mock_ingest_map_pipeline(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    sample = tmp_path / "sample.md"
    sample.write_text("# T\nA\nB", encoding="utf-8")
    parsed = run_ingest(sample, tmp_path / "papers", MockParser())
    paper_dir = tmp_path / "papers" / parsed.doc_id
    run_map(paper_dir, MockLLMClient())
    assert (paper_dir / "cognitive" / "candidate_graph.json").exists()
    content = (paper_dir / "cognitive" / "candidate_graph.json").read_text(encoding="utf-8")
    assert '"evidence_blocks"' in content
