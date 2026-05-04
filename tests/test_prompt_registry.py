from pathlib import Path

import pytest

from cuos.llm.prompt_registry import PromptRegistry


def test_prompt_registry_replace(tmp_path: Path) -> None:
    f = tmp_path / "a.md"
    f.write_text("hello {{name}}", encoding="utf-8")
    reg = PromptRegistry(tmp_path)
    assert reg.load("a.md", {"name": "cuos"}) == "hello cuos"


def test_prompt_registry_missing(tmp_path: Path) -> None:
    reg = PromptRegistry(tmp_path)
    with pytest.raises(FileNotFoundError):
        reg.load("missing.md")
