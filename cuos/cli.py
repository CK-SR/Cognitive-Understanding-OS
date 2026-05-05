from pathlib import Path

import typer
import yaml
from rich import print
from rich.table import Table

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
def main(
    config: Path = typer.Option(Path("config.yaml"), "--config"),
    debug: bool = typer.Option(False, "--debug"),
) -> None:
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
        state["config_path"].write_text(
            yaml.safe_dump(cfg.model_dump(), sort_keys=False), encoding="utf-8"
        )
    print(f"[green]Workspace initialized:[/green] {workspace}")
    print(f"[cyan]Config file:[/cyan] {state['config_path'].resolve()}")


@app.command()
def ingest(pdf_path: str, parser: str | None = typer.Option(None, "--parser")) -> None:
    cfg = _settings()
    workspace = Path(cfg.workspace_dir).resolve()
    parser_name = parser or cfg.parser.default
    parser_cfg = cfg.parser.adapters.get(parser_name, {})
    try:
        adapter = get_parser(parser_name, parser_cfg)
        parsed = run_ingest(
            Path(pdf_path), workspace / "papers", adapter, db_path=workspace / "cuos.db"
        )
    except ParserError as exc:
        if state["debug"]:
            raise
        print(
            f"[red]Parser error:[/red] {exc}. Try --parser mock or verify parser dependencies."
        )
        raise typer.Exit(code=2) from exc
    table = Table(title="Ingest Result")
    table.add_column("paper_id")
    table.add_column("output_dir")
    table.add_row(parsed.doc_id, str((workspace / "papers" / parsed.doc_id).resolve()))
    print(table)


@app.command("map")
def map_cmd(paper_id: str, llm: str | None = typer.Option(None, "--llm")) -> None:
    cfg = _settings()
    if llm:
        cfg.llm.provider = llm
    paper_dir = Path(cfg.workspace_dir).resolve() / "papers" / paper_id
    try:
        run_map(paper_dir, get_llm_client(cfg.llm), Path(cfg.prompts.dir))
    except FileNotFoundError as exc:
        if state["debug"]:
            raise
        print(f"[red]Missing file:[/red] {exc}. Run earlier pipeline steps first.")
        raise typer.Exit(code=2) from exc
    print(f"[green]Map completed:[/green] {(paper_dir / 'cognitive').resolve()}")


@app.command()
def session(
    paper_id: str,
    non_interactive_demo: bool = typer.Option(False, "--non-interactive-demo"),
) -> None:
    cfg = _settings()
    paper_dir = Path(cfg.workspace_dir).resolve() / "papers" / paper_id
    try:
        session_id = run_session(paper_dir, non_interactive_demo=non_interactive_demo)
    except FileNotFoundError as exc:
        if state["debug"]:
            raise
        print(f"[red]Missing file:[/red] {exc}. Run earlier pipeline steps first.")
        raise typer.Exit(code=2) from exc
    table = Table(title="Session Result")
    table.add_column("paper_id")
    table.add_column("session_id")
    table.add_row(paper_id, session_id)
    print(table)
    print(
        f"[cyan]Output:[/cyan] {(paper_dir / 'sessions' / f'{session_id}.json').resolve()}"
    )


@app.command()
def audit(
    paper_id: str,
    session: str = typer.Option(..., "--session"),
    llm: str | None = typer.Option(None, "--llm"),
) -> None:
    cfg = _settings()
    if llm:
        cfg.llm.provider = llm
    paper_dir = Path(cfg.workspace_dir).resolve() / "papers" / paper_id
    try:
        run_audit(
            paper_dir,
            session,
            get_llm_client(cfg.llm),
            prompt_dir=Path(cfg.prompts.dir),
            db_path=Path(cfg.workspace_dir).resolve() / "cuos.db",
        )
    except FileNotFoundError as exc:
        if state["debug"]:
            raise
        print(f"[red]Missing file:[/red] {exc}. Run earlier pipeline steps first.")
        raise typer.Exit(code=2) from exc
    print(
        f"[green]Audit completed:[/green] {(paper_dir / 'cognitive' / 'audit_report.md').resolve()}"
    )


@app.command()
def review(
    paper: str | None = typer.Option(None, "--paper"),
    llm: str | None = typer.Option(None, "--llm"),
    non_interactive_demo: bool = typer.Option(False, "--non-interactive-demo"),
) -> None:
    cfg = _settings()
    if llm:
        cfg.llm.provider = llm
    workspace = Path(cfg.workspace_dir).resolve()
    store = SQLiteStore(workspace / "cuos.db")
    completed = run_review(
        workspace,
        store,
        get_llm_client(cfg.llm),
        Path(cfg.prompts.dir),
        paper_id=paper,
        non_interactive_demo=non_interactive_demo,
    )
    table = Table(title="Review Completed Tasks")
    table.add_column("task_id")
    for task_id in completed:
        table.add_row(task_id)
    print(table)


if __name__ == "__main__":
    app()
