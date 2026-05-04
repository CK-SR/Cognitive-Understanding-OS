import pytest

from cuos.parsers.docling_parser import DoclingParser
from cuos.parsers.errors import ParserDependencyError
from cuos.parsers.marker_parser import MarkerParser
from cuos.parsers.mineru_parser import MineruParser


def test_docling_missing_dependency(tmp_path) -> None:
    parser = DoclingParser()
    with pytest.raises(ParserDependencyError):
        parser.parse(tmp_path / "in.md", tmp_path / "out")


def test_marker_missing_command(tmp_path) -> None:
    parser = MarkerParser({"command": "definitely_not_installed_marker_cmd"})
    with pytest.raises(ParserDependencyError):
        parser.parse(tmp_path / "in.pdf", tmp_path / "out")


def test_mineru_missing_command(tmp_path) -> None:
    parser = MineruParser({"command": "definitely_not_installed_mineru_cmd"})
    with pytest.raises(ParserDependencyError):
        parser.parse(tmp_path / "in.pdf", tmp_path / "out")
