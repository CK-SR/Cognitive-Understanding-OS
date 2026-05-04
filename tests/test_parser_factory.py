import pytest

from cuos.parsers.errors import ParserError
from cuos.parsers.factory import get_parser


def test_factory_supports_known_parsers() -> None:
    assert get_parser("mock").name == "mock"
    assert get_parser("docling", {}).name == "docling"
    assert get_parser("marker", {}).name == "marker"
    assert get_parser("mineru", {}).name == "mineru"


def test_factory_rejects_unknown_parser() -> None:
    with pytest.raises(ParserError):
        get_parser("unknown")
