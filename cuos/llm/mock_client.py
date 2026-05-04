class MockLLMClient:
    def generate_json(self, task_type: str, prompt_id: str, variables: dict) -> dict:
        if task_type == "problem_model":
            return {
                "doc_id": variables["doc_id"],
                "problem": "Improve low-resource graph learning",
                "motivation": "Existing methods are heavy",
                "key_claims": ["Lightweight model works", "Improves F1"],
            }
        if task_type == "graph_build":
            return {
                "doc_id": variables["doc_id"],
                "nodes": [
                    {"node_id": "n1", "type": "Problem", "content": "Low-resource graph learning", "source_blocks": ["b1"]},
                    {"node_id": "n2", "type": "Claim", "content": "Improves F1", "source_blocks": ["b3"]},
                ],
                "edges": [
                    {
                        "edge_id": "e1",
                        "source": "n2",
                        "target": "n1",
                        "relation": "solves",
                        "evidence_blocks": ["b3"],
                        "llm_confidence": 0.8,
                        "human_verified": False,
                    }
                ],
            }
        if task_type == "audit":
            return {
                "accuracy_score": 0.8,
                "completeness_score": 0.7,
                "depth_score": 0.6,
                "transfer_score": 0.5,
                "issues": ["Need clearer mechanism explanation"],
                "follow_up_question": "Why sparse encoder helps?",
            }
        return {}
