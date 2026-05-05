from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cuos.cognition.state_machine import SessionStage, ordered_question_states
from cuos.schemas.cognition import QuestionSet, SessionState, SessionTurn
from cuos.schemas.document import DocumentBlock, ParsedDocument
from cuos.schemas.graph import CognitiveGraph, CognitiveNode

QUESTION_TYPE_TO_STAGE: dict[str, SessionStage] = {
    "central_problem": SessionStage.CENTRAL_PROBLEM,
    "mechanism": SessionStage.MECHANISM_EXPLANATION,
    "formula": SessionStage.MECHANISM_EXPLANATION,
    "evidence": SessionStage.EVIDENCE_LINKING,
    "limitation": SessionStage.LIMITATION_CRITIQUE,
    "transfer": SessionStage.TRANSFER_APPLICATION,
}

FALLBACK_QUESTIONS: dict[SessionStage, str] = {
    SessionStage.CENTRAL_PROBLEM: "请用你自己的话复述这篇论文的中心问题和目标。",
    SessionStage.MECHANISM_EXPLANATION: "请解释论文的核心机制：输入是什么、关键步骤是什么、为什么有效？",
    SessionStage.EVIDENCE_LINKING: "请把一个核心结论和具体证据块连接起来，说明因果链。",
    SessionStage.LIMITATION_CRITIQUE: "请指出一个限制或反例，并解释会如何影响结论。",
    SessionStage.TRANSFER_APPLICATION: "如果迁移到你的项目，你会如何落地？请给出步骤。",
}

DEMO_ANSWERS: dict[SessionStage, str] = {
    SessionStage.CENTRAL_PROBLEM: "该工作尝试提升论文理解闭环的可验证性。",
    SessionStage.MECHANISM_EXPLANATION: "通过解析-建图-追问-审计形成循环。",
    SessionStage.EVIDENCE_LINKING: "图谱中的 claim 与 evidence_blocks 建立可回溯关系。",
    SessionStage.LIMITATION_CRITIQUE: "当前仅支持单论文，跨文献迁移能力有限。",
    SessionStage.TRANSFER_APPLICATION: "先接入项目文档，再逐步替换 parser 与 llm 适配器。",
}

STAGE_NODE_TYPES: dict[SessionStage, set[str]] = {
    SessionStage.CENTRAL_PROBLEM: {"Problem", "Motivation", "Gap", "PriorWork"},
    SessionStage.MECHANISM_EXPLANATION: {
        "Mechanism",
        "Module",
        "Formula",
        "Concept",
        "Claim",
    },
    SessionStage.EVIDENCE_LINKING: {
        "Claim",
        "Evidence",
        "Experiment",
        "Metric",
        "Result",
        "Figure",
        "Table",
        "Formula",
    },
    SessionStage.LIMITATION_CRITIQUE: {"Limitation", "Assumption", "Question", "Claim"},
    SessionStage.TRANSFER_APPLICATION: {
        "Application",
        "Mechanism",
        "Module",
        "Limitation",
        "Assumption",
    },
}

STAGE_EDGE_RELATIONS: dict[SessionStage, set[str]] = {
    SessionStage.CENTRAL_PROBLEM: {"motivates", "solves", "contrasts_with"},
    SessionStage.MECHANISM_EXPLANATION: {"depends_on", "derives_from", "supports"},
    SessionStage.EVIDENCE_LINKING: {"supports", "tests", "measured_by", "shown_in"},
    SessionStage.LIMITATION_CRITIQUE: {"limits", "assumes", "contradicts"},
    SessionStage.TRANSFER_APPLICATION: {"transfers_to", "limits", "assumes"},
}


def _load_key_questions(cognitive_dir: Path) -> dict[SessionStage, str]:
    key_questions_path = cognitive_dir / "key_questions.json"
    if not key_questions_path.exists():
        return {}
    question_set = QuestionSet.model_validate_json(
        key_questions_path.read_text(encoding="utf-8")
    )
    stage_questions: dict[SessionStage, str] = {}
    for q in question_set.questions:
        stage = QUESTION_TYPE_TO_STAGE.get(q.question_type)
        if stage is not None and stage not in stage_questions:
            stage_questions[stage] = q.question
    return stage_questions


def _read_multiline_answer() -> str:
    print("请输入回答（空行结束）：")
    lines: list[str] = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def run_session(paper_dir: Path, non_interactive_demo: bool = False) -> str:
    cognitive_dir = paper_dir / "cognitive"
    sessions_dir = paper_dir / "sessions"
    sessions_dir.mkdir(exist_ok=True)

    parsed_doc_path = paper_dir / "parsed_document.json"
    if not parsed_doc_path.exists():
        raise FileNotFoundError(
            f"parsed_document.json not found in {paper_dir}. Run 'cuos ingest' first."
        )
    parsed = ParsedDocument.model_validate_json(parsed_doc_path.read_text(encoding="utf-8"))

    candidate_graph_path = cognitive_dir / "candidate_graph.json"
    if not candidate_graph_path.exists():
        raise FileNotFoundError(
            f"candidate_graph.json not found in {cognitive_dir}. Run 'cuos map' first."
        )
    graph = CognitiveGraph.model_validate_json(candidate_graph_path.read_text(encoding="utf-8"))

    key_questions = _load_key_questions(cognitive_dir)

    session_id = f"session_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    turns: list[SessionTurn] = []
    for state in ordered_question_states():
        question = key_questions.get(state, FALLBACK_QUESTIONS[state])
        related_source_blocks, related_node_ids = _collect_related_context(
            state, parsed, graph
        )
        print(f"\n[{state}] {question}")
        if related_source_blocks:
            print("参考证据块已绑定到本轮回答，审计阶段会使用。")
        answer = (
            DEMO_ANSWERS[state] if non_interactive_demo else _read_multiline_answer()
        )
        turns.append(
            SessionTurn(
                state=state.value,
                question=question,
                answer=answer,
                related_source_blocks=related_source_blocks,
                related_node_ids=related_node_ids,
            )
        )

    session_state = SessionState(
        paper_id=paper_dir.name,
        session_id=session_id,
        current_state=SessionStage.DONE.value,
        turns=turns,
    )
    session_json_path = sessions_dir / f"{session_id}.json"
    session_md_path = sessions_dir / f"{session_id}.md"
    session_json_path.write_text(
        session_state.model_dump_json(indent=2), encoding="utf-8"
    )

    md_lines = [f"# Session {session_id}", f"Paper: {paper_dir.name}", ""]
    for i, turn in enumerate(turns, start=1):
        md_lines.extend(
            [
                f"## {i}. {turn.state}",
                f"**Q:** {turn.question}",
                "",
                "**Related nodes:** " + ", ".join(turn.related_node_ids),
                "",
                turn.answer,
                "",
            ]
        )
    session_md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return session_id


def _collect_related_context(
    stage: SessionStage,
    parsed: ParsedDocument,
    graph: CognitiveGraph,
    max_blocks: int = 10,
) -> tuple[list[dict[str, Any]], list[str]]:
    selected_nodes = _select_nodes_for_stage(stage, graph)
    selected_node_ids = [node.node_id for node in selected_nodes]

    block_ids: list[str] = []
    for node in selected_nodes:
        block_ids.extend(node.source_blocks)

    allowed_relations = STAGE_EDGE_RELATIONS.get(stage, set())
    for edge in graph.edges:
        if edge.relation not in allowed_relations:
            continue
        if edge.source in selected_node_ids or edge.target in selected_node_ids:
            block_ids.extend(edge.source_blocks)
            block_ids.extend(edge.evidence_blocks)
            if edge.source not in selected_node_ids:
                selected_node_ids.append(edge.source)
            if edge.target not in selected_node_ids:
                selected_node_ids.append(edge.target)

    contexts = _materialize_blocks(parsed.blocks, block_ids, max_blocks=max_blocks)
    if len(contexts) < max_blocks:
        contexts.extend(
            _graph_node_contexts(
                selected_nodes,
                selected_node_ids,
                max_items=max_blocks - len(contexts),
            )
        )
    return contexts[:max_blocks], selected_node_ids


def _select_nodes_for_stage(stage: SessionStage, graph: CognitiveGraph) -> list[CognitiveNode]:
    wanted_types = STAGE_NODE_TYPES.get(stage, set())
    nodes = [node for node in graph.nodes if node.type in wanted_types]
    return nodes[:8]


def _materialize_blocks(
    blocks: list[DocumentBlock], block_ids: list[str], max_blocks: int
) -> list[dict[str, Any]]:
    block_map = {block.block_id: block for block in blocks}
    seen: set[str] = set()
    contexts: list[dict[str, Any]] = []
    for block_id in block_ids:
        if block_id in seen:
            continue
        seen.add(block_id)
        block = block_map.get(block_id)
        if block is None:
            continue
        contexts.append(
            {
                "source": "document_block",
                "block_id": block.block_id,
                "type": block.type,
                "text": block.text,
                "page": block.page,
                "asset_path": block.asset_path,
            }
        )
        if len(contexts) >= max_blocks:
            break
    return contexts


def _graph_node_contexts(
    nodes: list[CognitiveNode], selected_node_ids: list[str], max_items: int
) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    seen = {context["block_id"] for context in contexts}
    for node in nodes:
        if max_items <= 0:
            break
        synthetic_id = f"graph_node:{node.node_id}"
        if synthetic_id in seen:
            continue
        contexts.append(
            {
                "source": "graph_node",
                "block_id": synthetic_id,
                "node_id": node.node_id,
                "type": node.type,
                "text": node.content,
                "source_blocks": node.source_blocks,
            }
        )
        if node.node_id not in selected_node_ids:
            selected_node_ids.append(node.node_id)
        max_items -= 1
    return contexts
