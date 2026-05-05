from collections.abc import Mapping
from typing import Any

from cuos.parsers.base import ParserAdapter
from cuos.parsers.docling_parser import DoclingParser
from cuos.parsers.errors import ParserError
from cuos.parsers.marker_parser import MarkerParser
from cuos.parsers.mineru_parser import MineruParser
from cuos.parsers.mock_parser import MockParser


def get_parser(name: str, config: Mapping[str, Any] | None = None) -> ParserAdapter:
    parser_name = name.strip().lower()
    parser_config = dict(config or {})

    if parser_name == "mock":
        return MockParser()
    if parser_name == "docling":
        return DoclingParser(parser_config)
    if parser_name == "marker":
        return MarkerParser(parser_config)
    if parser_name == "mineru":
        return MineruParser(parser_config)
    raise ParserError(
        f"Unknown parser '{name}'. Supported parsers: mock, docling, marker, mineru"
    )
