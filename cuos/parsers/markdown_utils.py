from __future__ import annotations

import re
from pathlib import Path

from cuos.schemas.document import DocumentBlock

_IMAGE_PATTERN = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)")
_FORMULA_STARTS = ("$$", "\\[", "\\(")
_FORMULA_ENDS = ("$$", "\\]", "\\)")
_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".svg"}


def markdown_to_blocks(markdown_text: str, assets_dir: Path | None = None) -> list[DocumentBlock]:
    """Convert Markdown into lightweight structured blocks.

    This is intentionally heuristic. It does not replace MinerU/Docling/Marker's
    native structured output, but it gives CUOS V1 a useful minimum structure for
    formulas, tables, figures, captions, sections, and paragraphs.
    """
    blocks: list[DocumentBlock] = []
    lines = markdown_text.splitlines()
    i = 0
    block_index = 1
    referenced_assets: set[str] = set()

    def next_id() -> str:
        nonlocal block_index
        block_id = f"b{block_index}"
        block_index += 1
        return block_id

    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.strip()
        if not line:
            i += 1
            continue

        if _is_image_line(line):
            block, asset_name = _image_block(next_id(), line, assets_dir)
            if asset_name:
                referenced_assets.add(asset_name)
            blocks.append(block)
            i += 1
            continue

        if _is_table_line(line):
            table_lines = [line]
            i += 1
            while i < len(lines) and _is_table_line(lines[i].strip()):
                table_lines.append(lines[i].strip())
                i += 1
            blocks.append(
                DocumentBlock(
                    block_id=next_id(),
                    type="table",
                    text="\n".join(table_lines),
                )
            )
            continue

        if _starts_formula(line):
            formula_lines = [line]
            i += 1
            if not _ends_formula(line) or _single_marker_only(line):
                while i < len(lines):
                    formula_lines.append(lines[i].strip())
                    if _ends_formula(lines[i].strip()):
                        i += 1
                        break
                    i += 1
            blocks.append(
                DocumentBlock(
                    block_id=next_id(),
                    type="formula",
                    text="\n".join(formula_lines),
                )
            )
            continue

        if _looks_like_formula(line):
            blocks.append(DocumentBlock(block_id=next_id(), type="formula", text=line))
            i += 1
            continue

        if line.startswith("#"):
            heading_text = line.lstrip("#").strip()
            block_type = "title" if line.startswith("# ") and not blocks else "section"
            blocks.append(
                DocumentBlock(block_id=next_id(), type=block_type, text=heading_text)
            )
            i += 1
            continue

        if _looks_like_caption(line):
            blocks.append(DocumentBlock(block_id=next_id(), type="caption", text=line))
            i += 1
            continue

        blocks.append(DocumentBlock(block_id=next_id(), type="paragraph", text=line))
        i += 1

    _append_unreferenced_asset_blocks(blocks, assets_dir, referenced_assets, block_index)
    return blocks


def _is_image_line(line: str) -> bool:
    return _IMAGE_PATTERN.search(line) is not None


def _image_block(
    block_id: str, line: str, assets_dir: Path | None
) -> tuple[DocumentBlock, str | None]:
    match = _IMAGE_PATTERN.search(line)
    if match is None:
        return DocumentBlock(block_id=block_id, type="figure", text=line), None
    alt = match.group("alt").strip() or None
    raw_path = match.group("path").strip().strip('"')
    asset_name = Path(raw_path).name
    asset_path = raw_path
    if assets_dir is not None:
        candidate = assets_dir / asset_name
        if candidate.exists():
            asset_path = str(candidate)
    return (
        DocumentBlock(
            block_id=block_id,
            type="figure",
            text=alt or line,
            asset_path=asset_path,
        ),
        asset_name,
    )


def _is_table_line(line: str) -> bool:
    if not line.startswith("|") or "|" not in line[1:]:
        return False
    return line.count("|") >= 2


def _starts_formula(line: str) -> bool:
    return line.startswith(_FORMULA_STARTS)


def _ends_formula(line: str) -> bool:
    return line.endswith(_FORMULA_ENDS)


def _single_marker_only(line: str) -> bool:
    return line in {"$$", "\\[", "\\("}


def _looks_like_formula(line: str) -> bool:
    if len(line) > 240:
        return False
    if line.startswith(("\\begin{equation}", "\\begin{align}", "\\begin{split}")):
        return True
    if any(token in line for token in ("\\frac", "\\sum", "\\prod", "\\int", "\\mathbf")):
        return True
    if re.search(r"[A-Za-z0-9_{}^\\]+\s*=\s*[-+A-Za-z0-9_{}^\\()/.]+", line):
        # Avoid classifying normal prose with '=' as formula unless it also has a math cue.
        math_cues = ("\\", "^", "_", "=", "/", "(", ")")
        return sum(1 for cue in math_cues if cue in line) >= 2
    return False


def _looks_like_caption(line: str) -> bool:
    lower = line.lower()
    return lower.startswith(("figure ", "fig. ", "fig ", "table ", "图", "表"))


def _append_unreferenced_asset_blocks(
    blocks: list[DocumentBlock],
    assets_dir: Path | None,
    referenced_assets: set[str],
    next_index: int,
) -> None:
    if assets_dir is None or not assets_dir.exists():
        return
    block_index = next_index
    for asset in sorted(assets_dir.iterdir()):
        if not asset.is_file() or asset.suffix.lower() not in _IMAGE_SUFFIXES:
            continue
        if asset.name in referenced_assets:
            continue
        blocks.append(
            DocumentBlock(
                block_id=f"b{block_index}",
                type="figure",
                text=f"Extracted image asset: {asset.name}",
                asset_path=str(asset),
            )
        )
        block_index += 1
