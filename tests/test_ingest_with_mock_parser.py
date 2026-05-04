import sqlite3
from pathlib import Path

from cuos.parsers.mock_parser import MockParser
from cuos.pipeline.ingest import run_ingest


def test_ingest_with_mock_parser_persists_document(tmp_path: Path) -> None:
    sample = tmp_path / "sample.md"
    sample.write_text("# Title\nline1\nline2", encoding="utf-8")

    db_path = tmp_path / "cuos.db"
    parsed = run_ingest(sample, tmp_path / "papers", MockParser(), db_path=db_path)

    assert parsed.doc_id.startswith("paper_")
    assert len(parsed.blocks) >= 2
    assert Path(parsed.markdown_path).exists()
    assert Path(parsed.structure_path).exists()

    conn = sqlite3.connect(db_path)
    rows = conn.execute("select doc_id from parsed_documents where doc_id=?", (parsed.doc_id,)).fetchall()
    conn.close()
    assert len(rows) == 1
