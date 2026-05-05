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


class MineruParser(ParserAdapter):
    name = "mineru"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

    @property
    def _server_url(self) -> str:
        return self.config.get("server_url", "")

    @property
    def _backend(self) -> str:
        return self.config.get("backend", "")

    @property
    def _api_key(self) -> str:
        return self.config.get("api_key", "")

    def _build_remote_cmd(
        self, source_path: Path, output_dir: Path, extra_args: list[str]
    ) -> list[str]:
        command = self.config.get("command", "mineru")
        backend = self._backend or "vlm-http-client"
        cmd = [
            command,
            "-p",
            str(source_path),
            "-o",
            str(output_dir),
            "-b",
            backend,
            "-u",
            self._server_url,
        ]
        if self._api_key:
            cmd.extend(["--api-key", self._api_key])
        cmd.extend(extra_args)
        return cmd

    def _build_local_cmd(
        self, command: str, source_path: Path, output_dir: Path, extra_args: list[str]
    ) -> list[str]:
        return [command, "-p", str(source_path), "-o", str(output_dir), *extra_args]

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

        if self._server_url:
            cmd = self._build_remote_cmd(source_path, raw_dir, extra_args)
        else:
            cmd = self._build_local_cmd(command, source_path, raw_dir, extra_args)

        timeout = self.config.get("timeout", 600)
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
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

        assets_dir = paper_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        for file in raw_dir.rglob("*"):
            if file.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
                shutil.copy2(file, assets_dir / file.name)

        blocks = markdown_to_blocks(markdown_text, assets_dir=assets_dir)

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

        report = {
            "parser_name": self.name,
            "command": command,
            "return_code": proc.returncode,
            "degraded": degraded,
            "warnings": []
            if not degraded
            else ["No structured JSON found; using heuristic Markdown blocks."],
            "normalized_block_types": sorted({block.type for block in blocks}),
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
