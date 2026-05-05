from typing import Literal

from pydantic import BaseModel, Field


class CognitiveNode(BaseModel):
    node_id: str
    type: Literal[
        "Problem",
        "Motivation",
        "PriorWork",
        "Gap",
        "Claim",
        "Concept",
        "Mechanism",
        "Formula",
        "Module",
        "Experiment",
        "Metric",
        "Result",
        "Figure",
        "Table",
        "Evidence",
        "Limitation",
        "Assumption",
        "Application",
        "Question",
    ]
    content: str
    source_blocks: list[str] = Field(default_factory=list)
    understanding_level: Literal["L0", "L1", "L2", "L3", "L4", "L5"] = "L0"
    human_verified: bool = False


class CognitiveEdge(BaseModel):
    edge_id: str
    source: str
    target: str
    relation: Literal[
        "solves",
        "motivates",
        "contrasts_with",
        "depends_on",
        "derives_from",
        "supports",
        "tests",
        "measured_by",
        "shown_in",
        "contradicts",
        "limits",
        "assumes",
        "transfers_to",
        "unclear_about",
    ]
    source_blocks: list[str] = Field(default_factory=list)
    evidence_blocks: list[str] = Field(default_factory=list)
    llm_confidence: float | None = None
    human_verified: bool = False


class CognitiveGraph(BaseModel):
    doc_id: str
    nodes: list[CognitiveNode]
    edges: list[CognitiveEdge]
