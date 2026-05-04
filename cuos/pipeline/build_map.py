import json
from pathlib import Path

from cuos.graph.builder import build_graph
from cuos.schemas.cognition import ProblemModel


def run_map(paper_dir: Path, llm) -> None:
    doc_id = paper_dir.name
    cognitive_dir = paper_dir / "cognitive"
    cognitive_dir.mkdir(exist_ok=True)

    problem = ProblemModel.model_validate(llm.generate_json("problem_model", "problem_model.md", {"doc_id": doc_id}))
    (cognitive_dir / "problem_model.json").write_text(problem.model_dump_json(indent=2), encoding="utf-8")

    graph = build_graph(llm.generate_json("graph_build", "graph_builder.md", {"doc_id": doc_id}))
    (cognitive_dir / "candidate_graph.json").write_text(graph.model_dump_json(indent=2), encoding="utf-8")
    (cognitive_dir / "key_questions.md").write_text("- What is the core mechanism?\n- Why does it work?\n", encoding="utf-8")
    (cognitive_dir / "reading_map.md").write_text("1. Read abstract\n2. Read method\n3. Read experiments\n", encoding="utf-8")
