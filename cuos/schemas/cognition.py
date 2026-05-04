from pydantic import BaseModel, Field


class ProblemModel(BaseModel):
    doc_id: str
    problem: str
    motivation: str
    key_claims: list[str] = Field(default_factory=list)


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
