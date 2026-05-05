from __future__ import annotations

import json
import re
from pathlib import Path

from cuos.graph.utils import export_graph_summary_md
from cuos.llm.prompt_registry import PromptRegistry
from cuos.schemas.cognition import ProblemModel, QuestionSet, ReadingMap
from cuos.schemas.document import ParsedDocument
from cuos.schemas.graph import CognitiveGraph

DEFAULT_MAX_INPUT_CHARS = 120000
_SECTION_KEYWORDS = (
    "abstract",
    "introduction",
    "background",
    "related work",
    "method",
    "methodology",
    "approach",
    "proposed",
    "model",
    "algorithm",
    "experiment",
    "evaluation",
    "ablation",
    "result",
    "analysis",
    "discussion",
    "limitation",
    "conclusion",
    "摘要",
    "引言",
    "背景",
    "相关工作",
    "方法",
    "模型",
    "算法",
    "实验",
    "评估",
    "消融",
    "结果",
    "分析",
    "讨论",
    "限制",
    "局限",
    "结论",
)


def _load_parsed_document(paper_dir: Path) -> ParsedDocument:
    return ParsedDocument.model_validate_json(
        (paper_dir / "parsed_document.json").read_text(encoding="utf-8")
    )


def _compress_markdown(text: str, max_input_chars: int) -> str:
    """Build a section-aware compact context for map-stage LLM calls.

    The previous V1 implementation used `text[:12000]`, which often kept only
    abstract/introduction and dropped method/experiment/limitations. This V1.1
    compressor is still simple and deterministic, but it keeps head, tail, and
    slices around important section keywords.
    """
    if max_input_chars <= 0 or len(text) <= max_input_chars:
        return text

    head_budget = int(max_input_chars * 0.32)
    tail_budget = int(max_input_chars * 0.23)
    middle_budget = max_input_chars - head_budget - tail_budget

    spans: list[tuple[int, int]] = [(0, min(len(text), head_budget))]
    spans.extend(_keyword_spans(text, middle_budget))
    spans.append((max(0, len(text) - tail_budget), len(text)))

    merged = _merge_spans(spans, len(text))
    parts: list[str] = []
    for start, end in merged:
        snippet = text[start:end].strip()
        if snippet:
            parts.append(f"\n\n<!-- CUOS_CONTEXT_SLICE {start}:{end} -->\n\n{snippet}")
    compact = "\n".join(parts).strip()
    if len(compact) > max_input_chars:
        return compact[:max_input_chars]
    return compact


def _keyword_spans(text: str, budget: int) -> list[tuple[int, int]]:
    if budget <= 0:
        return []
    lower_text = text.lower()
    positions: list[int] = []
    for keyword in _SECTION_KEYWORDS:
        keyword_lower = keyword.lower()
        for match in re.finditer(re.escape(keyword_lower), lower_text):
            positions.append(match.start())
            break
    if not positions:
        return []

    positions = sorted(set(positions))
    each = max(1200, budget // max(len(positions), 1))
    return [
        (max(0, pos - each // 3), min(len(text), pos + each * 2 // 3))
        for pos in positions
    ]


def _merge_spans(spans: list[tuple[int, int]], text_len: int) -> list[tuple[int, int]]:
    cleaned = sorted((max(0, s), min(text_len, e)) for s, e in spans if e > s)
    merged: list[tuple[int, int]] = []
    for start, end in cleaned:
        if not merged or start > merged[-1][1] + 200:
            merged.append((start, end))
        else:
            prev_start, prev_end = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end))
    return merged


def run_map(
    paper_dir: Path,
    llm,
    prompt_dir: Path = Path("prompts"),
    max_input_chars: int = DEFAULT_MAX_INPUT_CHARS,
    interaction_language: str = "zh-CN",
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

    common_vars = {
        "document_markdown": compact_markdown,
        "interaction_language": interaction_language,
    }
    problem_prompt = registry.load("problem_model.md", common_vars)
    problem = llm.chat_json([{"role": "user", "content": problem_prompt}], ProblemModel)
    (cognitive_dir / "problem_model.json").write_text(
        problem.model_dump_json(indent=2), encoding="utf-8"
    )

    graph_prompt = registry.load(
        "graph_builder.md",
        {
            **common_vars,
            "problem_model_json": problem.model_dump_json(indent=2),
        },
    )
    graph = llm.chat_json([{"role": "user", "content": graph_prompt}], CognitiveGraph)
    (cognitive_dir / "candidate_graph.json").write_text(
        graph.model_dump_json(indent=2), encoding="utf-8"
    )

    question_prompt = registry.load(
        "socratic_question.md",
        {
            "candidate_graph_json": graph.model_dump_json(indent=2),
            "interaction_language": interaction_language,
        },
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
            problem.reading_strategy,
            "检查候选图谱中的 Claim -> Evidence -> Limitation 证据链。",
            "进入 session，用中文闭卷复述并接受审计。",
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
                "markdown_chars": len(markdown),
                "compact_markdown_chars": len(compact_markdown),
                "max_input_chars": max_input_chars,
                "interaction_language": interaction_language,
                "nodes": len(graph.nodes),
                "edges": len(graph.edges),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
