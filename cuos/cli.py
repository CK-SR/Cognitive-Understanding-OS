import json
from pathlib import Path

import typer
import yaml
from rich import print

from cuos.config.settings import Settings
from cuos.llm.factory import get_llm_client
from cuos.parsers.errors import ParserError
from cuos.parsers.factory import get_parser
from cuos.pipeline.audit import run_audit
from cuos.pipeline.build_map import run_map
from cuos.pipeline.ingest import run_ingest
from cuos.pipeline.review import run_review
from cuos.pipeline.session import run_session
from cuos.storage.sqlite_store import SQLiteStore
from cuos.storage.workspace import init_workspace

app = typer.Typer()
state = {"config_path": Path("config.yaml"), "debug": False}


@app.callback()
def main(config: Path = typer.Option(Path("config.yaml"), "--config"), debug: bool = typer.Option(False, "--debug")) -> None:
    state["config_path"] = config
    state["debug"] = debug


def _settings() -> Settings:
    return Settings.from_file(state["config_path"])


@app.command()
def init() -> None:
    cfg = _settings()
    workspace = Path(cfg.workspace_dir).resolve()
    init_workspace(workspace)
    if not state["config_path"].exists():
        state["config_path"].write_text(yaml.safe_dump(cfg.model_dump(), sort_keys=False), encoding="utf-8")
    print(f"[green]Workspace initialized:[/green] {workspace}")


@app.command()
def ingest(pdf_path: str, parser: str | None = typer.Option(None, "--parser")) -> None:
    cfg = _settings()
    workspace = Path(cfg.workspace_dir).resolve()
    parser_name = parser or cfg.parser.default
    parser_cfg = cfg.parser.adapters.get(parser_name, {})
    try:
        adapter = get_parser(parser_name, parser_cfg)
        parsed = run_ingest(Path(pdf_path), workspace / "papers", adapter, db_path=workspace / "cuos.db")
    except ParserError as exc:
        if state["debug"]:
            raise
        print(f"[red]Parser error:[/red] {exc}")
        raise typer.Exit(code=2) from exc
    print(f"[green]Ingested[/green] {pdf_path} -> {parsed.doc_id} ({parser_name})")


@app.command("map")
def map_cmd(paper_id: str, llm: str | None = typer.Option(None, "--llm")) -> None:
    cfg = _settings()
    if llm:
        cfg.llm.provider = llm
    client = get_llm_client(cfg.llm)
    run_map(Path(cfg.workspace_dir).resolve() / "papers" / paper_id, client, Path(cfg.prompts.dir))
    print(f"[green]Mapped[/green] {paper_id}")


@app.command()
def session(paper_id: str) -> None:
    cfg = _settings()
    paper_dir = Path(cfg.workspace_dir).resolve() / "papers" / paper_id
    questions = (paper_dir / "cognitive" / "key_questions.md").read_text(encoding="utf-8")
    print("[bold]Candidate Questions[/bold]\n" + questions)
    answer = typer.prompt("Your answer")
    saved = run_session(paper_dir, answer)
    print(f"Saved session: {saved}")


@app.command()
def audit(paper_id: str) -> None:
    cfg = _settings()
    paper_dir = Path(cfg.workspace_dir).resolve() / "papers" / paper_id
    session_files = sorted((paper_dir / "sessions").glob("session_*.json"))
    if not session_files:
        raise typer.BadParameter("No session found. Run session first.")
    latest = json.loads(session_files[-1].read_text(encoding="utf-8"))
    run_audit(paper_dir, latest["answer"], get_llm_client(cfg.llm))
    print(f"[green]Audit completed[/green] {paper_id}")


@app.command()
def review() -> None:
    cfg = _settings()
    store = SQLiteStore(Path(cfg.workspace_dir).resolve() / "cuos.db")
    tasks = run_review(store)
    print("[bold]Today review tasks[/bold]")
    for t in tasks:
        print(f"- {t}")


if __name__ == "__main__":
    app()
