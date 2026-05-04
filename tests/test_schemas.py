import pytest
from pydantic import ValidationError

from cuos.schemas.graph import CognitiveGraph


def test_graph_schema_valid() -> None:
    payload = {
        "doc_id": "p1",
        "nodes": [{"node_id": "n1", "type": "Problem", "content": "x", "source_blocks": ["b1"]}],
        "edges": [{"edge_id": "e1", "source": "n1", "target": "n1", "relation": "supports", "evidence_blocks": ["b1"]}],
    }
    graph = CognitiveGraph.model_validate(payload)
    assert graph.doc_id == "p1"


def test_graph_schema_invalid_relation() -> None:
    with pytest.raises(ValidationError):
        CognitiveGraph.model_validate({"doc_id": "p1", "nodes": [], "edges": [{"edge_id": "e", "source": "a", "target": "b", "relation": "bad", "evidence_blocks": []}]})
