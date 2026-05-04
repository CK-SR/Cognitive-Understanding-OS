from pathlib import Path

from cuos.storage.workspace import init_workspace


def test_init_workspace(tmp_path: Path) -> None:
    init_workspace(tmp_path)
    assert (tmp_path / "cuos.db").exists()
    assert (tmp_path / "papers").exists()
