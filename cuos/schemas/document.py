from typing import Literal

from pydantic import BaseModel


class DocumentBlock(BaseModel):
    block_id: str
    type: Literal[
        "title",
        "section",
        "paragraph",
        "formula",
        "table",
        "figure",
        "caption",
        "reference",
        "unknown",
    ]
    text: str | None = None
    page: int | None = None
    bbox: list[float] | None = None
    asset_path: str | None = None


class ParsedDocument(BaseModel):
    doc_id: str
    title: str | None = None
    source_path: str
    markdown_path: str
    structure_path: str
    assets_dir: str
    blocks: list[DocumentBlock]
