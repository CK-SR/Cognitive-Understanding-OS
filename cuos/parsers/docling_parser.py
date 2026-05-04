import json
import uuid
from pathlib import Path
from typing import Any

from cuos.parsers.base import ParserAdapter
from cuos.parsers.errors import ParserDependencyError
from cuos.schemas.document import DocumentBlock, ParsedDocument


class DoclingParser(ParserAdapter):
    name = "docling"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    def parse(self, source_path: Path, output_dir: Path) -> ParsedDocument:
        try:
            import docling  # type: ignore  # noqa: F401
        except ImportError as exc:
            raise ParserDependencyError(
                "Docling is not installed. Install with `pip install docling` (or your managed env command)."
            ) from exc

        paper_id = f"paper_{uuid.uuid4().hex[:8]}"
        paper_dir = output_dir / paper_id
        paper_dir.mkdir(parents=True, exist_ok=True)
        assets_dir = paper_dir / "assets"
        assets_dir.mkdir(exist_ok=True)

        markdown_text = source_path.read_text(encoding="utf-8", errors="ignore")
        md_path = paper_dir / "full.md"
        md_path.write_text(markdown_text, encoding="utf-8")

        blocks = _markdown_blocks(markdown_text)
        structure_path = paper_dir / "structure.json"
        structure_path.write_text(json.dumps([b.model_dump() for b in blocks], ensure_ascii=False, indent=2), encoding="utf-8")

        report = {
            "parser_name": self.name,
            "degraded": True,
            "warnings": ["Docling adapter fallback: markdown-only block extraction in this version."],
        }
        (paper_dir / "parse_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        return ParsedDocument(
            doc_id=paper_id,
            title=blocks[0].text if blocks else None,
            source_path=str(source_path),
            markdown_path=str(md_path),
            structure_path=str(structure_path),
            assets_dir=str(assets_dir),
            blocks=blocks,
        )


def _markdown_blocks(markdown_text: str) -> list[DocumentBlock]:
    lines = [line.strip() for line in markdown_text.splitlines() if line.strip()]
    return [DocumentBlock(block_id=f"b{i}", type="paragraph", text=line, page=1) for i, line in enumerate(lines, start=1)]
