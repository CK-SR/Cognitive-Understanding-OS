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
from cuos.parsers.markdown_utils import markdown_to_blocks
from cuos.schemas.document import ParsedDocument


class MarkerParser(ParserAdapter):
    name = "marker"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    def parse(self, source_path: Path, output_dir: Path) -> ParsedDocument:
        command = self.config.get("command", "marker_single")
        extra_args = self.config.get("extra_args", [])
        if shutil.which(command) is None:
            raise ParserDependencyError(
                f"Marker command not found: '{command}'. Please install Marker and update parser.adapters.marker.command."
            )

        paper_id = f"paper_{uuid.uuid4().hex[:8]}"
        paper_dir = output_dir / paper_id
        paper_dir.mkdir(parents=True, exist_ok=True)
        raw_dir = paper_dir / "raw_marker"
        raw_dir.mkdir(exist_ok=True)

        cmd = [command, str(source_path), "--output_dir", str(raw_dir), *extra_args]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise ParserExecutionError(
                f"Marker execution failed (code={proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}"
            )

        parsed = _normalize_output(paper_dir, raw_dir, source_path, command, proc.returncode)
        if not parsed.blocks:
            raise ParserOutputError("Marker parser produced no content blocks.")
        return parsed


def _normalize_output(
    paper_dir: Path,
    raw_dir: Path,
    source_path: Path,
    command: str,
    return_code: int,
) -> ParsedDocument:
    markdown_candidates = list(raw_dir.rglob("*.md"))
    json_candidates = list(raw_dir.rglob("*.json"))

    if not markdown_candidates:
        raise ParserOutputError("Marker output did not include any markdown file.")
    md_src = markdown_candidates[0]
    markdown_text = md_src.read_text(encoding="utf-8", errors="ignore")
    md_dst = paper_dir / "full.md"
    md_dst.write_text(markdown_text, encoding="utf-8")

    assets_dir = paper_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    for img in raw_dir.rglob("*"):
        if img.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
            shutil.copy2(img, assets_dir / img.name)

    blocks = markdown_to_blocks(markdown_text, assets_dir=assets_dir)

    structure_dst = paper_dir / "structure.json"
    # Preserve original parser JSON when available, but ensure ParsedDocument.blocks
    # has CUOS-normalized Markdown blocks with formula/table/figure types.
    if json_candidates:
        structure_dst.write_text(
            json_candidates[0].read_text(encoding="utf-8", errors="ignore"),
            encoding="utf-8",
        )
    else:
        structure_dst.write_text(
            json.dumps([b.model_dump() for b in blocks], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    report = {
        "parser_name": "marker",
        "command": command,
        "return_code": return_code,
        "degraded": not bool(json_candidates),
        "warnings": []
        if json_candidates
        else ["No JSON structure found; downgraded to heuristic Markdown blocks."],
        "normalized_block_types": sorted({block.type for block in blocks}),
    }
    (paper_dir / "parse_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return ParsedDocument(
        doc_id=paper_dir.name,
        title=blocks[0].text if blocks else None,
        source_path=str(source_path),
        markdown_path=str(md_dst),
        structure_path=str(structure_dst),
        assets_dir=str(assets_dir),
        blocks=blocks,
    )
