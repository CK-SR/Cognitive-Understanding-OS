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
    questions: list[str] = Field(default_factory=list)
    latest_answer_path: str | None = None


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
