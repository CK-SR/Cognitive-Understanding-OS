import sqlite3
from pathlib import Path

from cuos.parsers.base import ParserAdapter
from cuos.schemas.document import ParsedDocument


def run_ingest(
    file_path: Path,
    papers_dir: Path,
    parser: ParserAdapter,
    db_path: Path | None = None,
) -> ParsedDocument:
    parsed = parser.parse(source_path=file_path, output_dir=papers_dir)
    paper_dir = Path(parsed.markdown_path).parent
    (paper_dir / "parsed_document.json").write_text(
        parsed.model_dump_json(indent=2), encoding="utf-8"
    )
    if db_path is not None:
        conn = sqlite3.connect(db_path)
        conn.execute(
            "create table if not exists parsed_documents (doc_id text primary key, source_path text, markdown_path text, structure_path text, assets_dir text)"
        )
        conn.execute(
            "insert or replace into parsed_documents (doc_id, source_path, markdown_path, structure_path, assets_dir) values (?,?,?,?,?)",
            (
                parsed.doc_id,
                parsed.source_path,
                parsed.markdown_path,
                parsed.structure_path,
                parsed.assets_dir,
            ),
        )
        conn.commit()
        conn.close()
    return parsed
