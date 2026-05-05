from __future__ import annotations

from pydantic import BaseModel

from cuos.llm.base import LLMClient
from cuos.schemas.cognition import ProblemModel, QuestionSet, ReadingMap
from cuos.schemas.graph import CognitiveGraph


class MockLLMClient(LLMClient):
    def generate_json(self, task_type: str, prompt_id: str, variables: dict) -> dict:
        if task_type == "audit":
            return {
                "accuracy_score": 0.8,
                "completeness_score": 0.7,
                "depth_score": 0.6,
                "transfer_score": 0.5,
                "issues": ["Need clearer mechanism explanation"],
                "missing_evidence": ["b3"],
                "corrected_understanding": "Mechanism must be connected to explicit evidence blocks.",
                "follow_up_question": "Why sparse encoder helps?",
                "suggested_understanding_level": "L2",
            }
        return {}

    def chat_text(self, messages: list[dict], **kwargs: object) -> str:
        return "mock-text"

    def chat_json(
        self, messages: list[dict], schema_model: type[BaseModel], **kwargs: object
    ) -> BaseModel:
        name = schema_model.__name__
        if name == "ProblemModel":
            return ProblemModel(
                central_problem="Improve low-resource graph learning",
                why_important="Reduce compute and data requirements.",
                prior_methods=["Large pretraining", "Heavy GNN ensembles"],
                gap="High cost and weak transfer to small datasets.",
                core_claims=["Lightweight design improves F1"],
                core_mechanism="Sparse encoder with robust objectives.",
                key_evidence_candidates=["b3", "b4"],
                limitations=["Limited domains evaluated"],
                reading_strategy="Read method then ablations.",
            )
        if name == "CognitiveGraph":
            return CognitiveGraph.model_validate(
                {
                    "doc_id": "mock-doc",
                    "nodes": [
                        {
                            "node_id": "n1",
                            "type": "Problem",
                            "content": "Low-resource graph learning",
                            "source_blocks": ["b1"],
                        },
                        {
                            "node_id": "n2",
                            "type": "Claim",
                            "content": "Improves F1",
                            "source_blocks": ["b3"],
                        },
                    ],
                    "edges": [
                        {
                            "edge_id": "e1",
                            "source": "n2",
                            "target": "n1",
                            "relation": "supports",
                            "source_blocks": ["b3"],
                            "evidence_blocks": ["b3"],
                            "llm_confidence": 0.7,
                            "human_verified": False,
                        }
                    ],
                }
            )
        if name == "QuestionSet":
            return QuestionSet(questions=[])
        if name == "ReadingMap":
            return ReadingMap(steps=["Read abstract", "Read method", "Read evidence"])
        if name == "AuditResult":
            return schema_model.model_validate(
                {
                    "accuracy_score": 0.8,
                    "completeness_score": 0.7,
                    "depth_score": 0.6,
                    "transfer_score": 0.5,
                    "issues": ["Need clearer mechanism explanation"],
                    "missing_evidence": ["b3"],
                    "corrected_understanding": "Mechanism must be connected to explicit evidence blocks.",
                    "follow_up_question": "Why sparse encoder helps?",
                    "suggested_understanding_level": "L2",
                }
            )
        return schema_model.model_validate({})
