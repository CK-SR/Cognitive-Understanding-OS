from typing import Any

from pydantic import BaseModel, Field


class ProblemModel(BaseModel):
    central_problem: str
    why_important: str
    prior_methods: list[str] = Field(default_factory=list)
    gap: str
    core_claims: list[str] = Field(default_factory=list)
    core_mechanism: str
    key_evidence_candidates: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    reading_strategy: str


class KeyQuestion(BaseModel):
    question_type: str
    question: str


class QuestionSet(BaseModel):
    questions: list[KeyQuestion] = Field(default_factory=list)


class ReadingMap(BaseModel):
    steps: list[str] = Field(default_factory=list)


class SessionState(BaseModel):
    paper_id: str
    session_id: str
    current_state: str
    turns: list["SessionTurn"] = Field(default_factory=list)


class SessionTurn(BaseModel):
    state: str
    question: str
    answer: str
    # V1.1: store grounded evidence snippets, not just block ids. This keeps
    # audit from judging only from the user's answer and a high-level graph.
    related_source_blocks: list[dict[str, Any]] = Field(default_factory=list)
    related_node_ids: list[str] = Field(default_factory=list)


class UserAnswer(BaseModel):
    paper_id: str
    answer: str
    timestamp: str


class ReviewTask(BaseModel):
    task_id: str
    paper_id: str
    question: str
    due_date: str
    status: str = "pending"


class UnderstandingState(BaseModel):
    paper_id: str
    level: str
    weak_points: list[str] = Field(default_factory=list)
    updated_from_session: str | None = None
    # Paper-level state above is preserved for compatibility. The following
    # fields make the understanding state graph-aware.
    node_levels: dict[str, str] = Field(default_factory=dict)
    weak_nodes: list[str] = Field(default_factory=list)
    node_weak_points: dict[str, list[str]] = Field(default_factory=dict)
