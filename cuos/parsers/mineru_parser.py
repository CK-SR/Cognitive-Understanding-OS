import json
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any

from cuos.parsers.base import ParserAdapter
from cuos.parsers.errors import (
    ParserDependencyError,
    ParserExecutionError,
    ParserOutputError,
)
from cuos.schemas.document import DocumentBlock, ParsedDocument


class MineruParser(ParserAdapter):
    name = "mineru"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    def parse(self, source_path: Path, output_dir: Path) -> ParsedDocument:
        command = self.config.get("command", "magic-pdf")
        extra_args = self.config.get("extra_args", [])
        if shutil.which(command) is None:
            raise ParserDependencyError(
                f"MinerU command not found: '{command}'. Please install MinerU/magic-pdf and configure parser.adapters.mineru.command."
            )

        paper_id = f"paper_{uuid.uuid4().hex[:8]}"
        paper_dir = output_dir / paper_id
        paper_dir.mkdir(parents=True, exist_ok=True)
        raw_dir = paper_dir / "raw_mineru"
        raw_dir.mkdir(exist_ok=True)

        cmd = [command,"-p", str(source_path), "-o", str(raw_dir), *extra_args]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise ParserExecutionError(
                f"MinerU execution failed (code={proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}"
            )

        markdown_candidates = list(raw_dir.rglob("*.md"))
        if not markdown_candidates:
            raise ParserOutputError("MinerU output did not include markdown.")

        md_src = markdown_candidates[0]
        markdown_text = md_src.read_text(encoding="utf-8", errors="ignore")
        md_dst = paper_dir / "full.md"
        md_dst.write_text(markdown_text, encoding="utf-8")

        blocks = [
            DocumentBlock(block_id=f"b{i}", type="paragraph", text=t, page=1)
            for i, t in enumerate(
                [
                    line_text.strip()
                    for line_text in markdown_text.splitlines()
                    if line_text.strip()
                ],
                1,
            )
        ]

        json_candidates = list(raw_dir.rglob("*.json"))
        structure_dst = paper_dir / "structure.json"
        degraded = True
        if json_candidates:
            structure_dst.write_text(
                json_candidates[0].read_text(encoding="utf-8", errors="ignore"),
                encoding="utf-8",
            )
            degraded = False
        else:
            structure_dst.write_text(
                json.dumps(
                    [b.model_dump() for b in blocks], ensure_ascii=False, indent=2
                ),
                encoding="utf-8",
            )

        assets_dir = paper_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        for file in raw_dir.rglob("*"):
            if file.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
                shutil.copy2(file, assets_dir / file.name)

        report = {
            "parser_name": self.name,
            "command": command,
            "return_code": proc.returncode,
            "degraded": degraded,
            "warnings": []
            if not degraded
            else ["No structured JSON found; using markdown paragraph blocks."],
        }
        (paper_dir / "parse_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        return ParsedDocument(
            doc_id=paper_id,
            title=blocks[0].text if blocks else None,
            source_path=str(source_path),
            markdown_path=str(md_dst),
            structure_path=str(structure_dst),
            assets_dir=str(assets_dir),
            blocks=blocks,
        )
