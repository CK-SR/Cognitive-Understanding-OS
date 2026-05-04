from pathlib import Path

from cuos.parsers.base import ParserAdapter
from cuos.schemas.document import ParsedDocument


def run_ingest(file_path: Path, papers_dir: Path, parser: ParserAdapter) -> ParsedDocument:
    return parser.parse(file_path=file_path, output_dir=papers_dir)
