from __future__ import annotations

import json
from pathlib import Path

from cuos.graph.utils import export_graph_summary_md
from cuos.llm.prompt_registry import PromptRegistry
from cuos.schemas.cognition import ProblemModel, QuestionSet, ReadingMap
from cuos.schemas.document import ParsedDocument
from cuos.schemas.graph import CognitiveGraph


def _load_parsed_document(paper_dir: Path) -> ParsedDocument:
    return ParsedDocument.model_validate_json(
        (paper_dir / "parsed_document.json").read_text(encoding="utf-8")
    )


def _compress_markdown(text: str, max_input_chars: int) -> str:
    return text[:max_input_chars]


def run_map(
    paper_dir: Path,
    llm,
    prompt_dir: Path = Path("prompts"),
    max_input_chars: int = 12000,
) -> None:
    parsed_doc_path = paper_dir / "parsed_document.json"
    if not parsed_doc_path.exists():
        raise FileNotFoundError(
            f"parsed_document.json not found in {paper_dir}. Run 'cuos ingest' first."
        )
    parsed = _load_parsed_document(paper_dir)
    cognitive_dir = paper_dir / "cognitive"
    cognitive_dir.mkdir(exist_ok=True)
    registry = PromptRegistry(prompt_dir)

    markdown = Path(parsed.markdown_path).read_text(encoding="utf-8")
    compact_markdown = _compress_markdown(markdown, max_input_chars)

    problem_prompt = registry.load(
        "problem_model.md", {"document_markdown": compact_markdown}
    )
    problem = llm.chat_json([{"role": "user", "content": problem_prompt}], ProblemModel)
    (cognitive_dir / "problem_model.json").write_text(
        problem.model_dump_json(indent=2), encoding="utf-8"
    )

    graph_prompt = registry.load(
        "graph_builder.md",
        {
            "document_markdown": compact_markdown,
            "problem_model_json": problem.model_dump_json(indent=2),
        },
    )
    graph = llm.chat_json([{"role": "user", "content": graph_prompt}], CognitiveGraph)
    (cognitive_dir / "candidate_graph.json").write_text(
        graph.model_dump_json(indent=2), encoding="utf-8"
    )

    question_prompt = registry.load(
        "socratic_question.md",
        {"candidate_graph_json": graph.model_dump_json(indent=2)},
    )
    questions = llm.chat_json(
        [{"role": "user", "content": question_prompt}], QuestionSet
    )
    (cognitive_dir / "key_questions.json").write_text(
        questions.model_dump_json(indent=2), encoding="utf-8"
    )
    (cognitive_dir / "key_questions.md").write_text(
        "\n".join(f"- {q.question}" for q in questions.questions), encoding="utf-8"
    )

    reading_map = ReadingMap(
        steps=[
            "Read problem statement",
            "Read mechanism",
            "Read evidence & limitations",
        ]
    )
    (cognitive_dir / "reading_map.md").write_text(
        "\n".join(f"{i + 1}. {s}" for i, s in enumerate(reading_map.steps)),
        encoding="utf-8",
    )
    (cognitive_dir / "graph_summary.md").write_text(
        export_graph_summary_md(graph), encoding="utf-8"
    )
    (cognitive_dir / "map_trace.json").write_text(
        json.dumps(
            {
                "doc_id": parsed.doc_id,
                "nodes": len(graph.nodes),
                "edges": len(graph.edges),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
