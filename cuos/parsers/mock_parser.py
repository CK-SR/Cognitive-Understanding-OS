import json
import uuid
from pathlib import Path

from cuos.parsers.base import ParserAdapter
from cuos.schemas.document import DocumentBlock, ParsedDocument


class MockParser(ParserAdapter):
    name = "mock"

    def parse(self, source_path: Path, output_dir: Path) -> ParsedDocument:
        paper_id = f"paper_{uuid.uuid4().hex[:8]}"
        paper_dir = output_dir / paper_id
        paper_dir.mkdir(parents=True, exist_ok=True)

        text = source_path.read_text(encoding="utf-8")
        raw_name = "raw_input.txt"
        (paper_dir / raw_name).write_text(text, encoding="utf-8")
        (paper_dir / "full.md").write_text(text, encoding="utf-8")

        blocks = [
            DocumentBlock(block_id=f"b{i}", type="paragraph", text=line, page=1)
            for i, line in enumerate(
                [line_text for line_text in text.splitlines() if line_text.strip()],
                start=1,
            )
        ]
        structure_path = paper_dir / "structure.json"
        structure_path.write_text(
            json.dumps([b.model_dump() for b in blocks], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (paper_dir / "assets").mkdir(exist_ok=True)
        (paper_dir / "parse_report.json").write_text(
            json.dumps({"status": "ok", "parser": "mock"}, indent=2), encoding="utf-8"
        )

        return ParsedDocument(
            doc_id=paper_id,
            title=blocks[0].text if blocks else None,
            source_path=str(source_path),
            markdown_path=str(paper_dir / "full.md"),
            structure_path=str(structure_path),
            assets_dir=str(paper_dir / "assets"),
            blocks=blocks,
        )
