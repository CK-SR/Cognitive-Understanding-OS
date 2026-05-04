from pydantic import BaseModel, Field


class AuditResult(BaseModel):
    accuracy_score: float
    completeness_score: float
    depth_score: float
    transfer_score: float
    issues: list[str] = Field(default_factory=list)
    follow_up_question: str | None = None
