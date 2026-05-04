from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from cuos.cognition.state_machine import SessionStage, ordered_question_states
from cuos.schemas.cognition import SessionState, SessionTurn
from cuos.schemas.document import ParsedDocument


STATE_QUESTIONS: dict[SessionStage, str] = {
    SessionStage.CENTRAL_PROBLEM: "请用你自己的话复述这篇论文的中心问题和目标。",
    SessionStage.MECHANISM_EXPLANATION: "请解释论文的核心机制：输入是什么、关键步骤是什么、为什么有效？",
    SessionStage.EVIDENCE_LINKING: "请把一个核心结论和具体证据块连接起来，说明因果链。",
    SessionStage.LIMITATION_CRITIQUE: "请指出一个限制或反例，并解释会如何影响结论。",
    SessionStage.TRANSFER_APPLICATION: "如果迁移到你的项目，你会如何落地？请给出步骤。",
}

DEMO_ANSWERS: dict[SessionStage, str] = {
    SessionStage.CENTRAL_PROBLEM: "该工作尝试提升论文理解闭环的可验证性。",
    SessionStage.MECHANISM_EXPLANATION: "通过解析-建图-追问-审计-复习形成循环。",
    SessionStage.EVIDENCE_LINKING: "图谱中的 claim 与 evidence_blocks 建立可回溯关系。",
    SessionStage.LIMITATION_CRITIQUE: "当前仅支持单论文，跨文献迁移能力有限。",
    SessionStage.TRANSFER_APPLICATION: "先接入项目文档，再逐步替换 parser 与 llm 适配器。",
}


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

    _ = ParsedDocument.model_validate_json((paper_dir / "parsed_document.json").read_text(encoding="utf-8"))
    _ = (cognitive_dir / "candidate_graph.json").read_text(encoding="utf-8")
    _ = (cognitive_dir / "key_questions.json").read_text(encoding="utf-8")

    session_id = f"session_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    turns: list[SessionTurn] = []
    for state in ordered_question_states():
        question = STATE_QUESTIONS[state]
        print(f"\n[{state}] {question}")
        answer = DEMO_ANSWERS[state] if non_interactive_demo else _read_multiline_answer()
        turns.append(SessionTurn(state=state.value, question=question, answer=answer, related_source_blocks=[]))

    session_state = SessionState(paper_id=paper_dir.name, session_id=session_id, current_state=SessionStage.DONE.value, turns=turns)
    session_json_path = sessions_dir / f"{session_id}.json"
    session_md_path = sessions_dir / f"{session_id}.md"
    session_json_path.write_text(session_state.model_dump_json(indent=2), encoding="utf-8")

    md_lines = [f"# Session {session_id}", f"Paper: {paper_dir.name}", ""]
    for i, turn in enumerate(turns, start=1):
        md_lines.extend([f"## {i}. {turn.state}", f"**Q:** {turn.question}", "", turn.answer, ""])
    session_md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return session_id
