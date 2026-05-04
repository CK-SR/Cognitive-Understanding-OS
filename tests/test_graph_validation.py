from cuos.graph.utils import find_unverified_edges, validate_graph_references
from cuos.schemas.document import DocumentBlock, ParsedDocument
from cuos.schemas.graph import CognitiveGraph


def test_graph_validation_and_unverified() -> None:
    doc = ParsedDocument(doc_id="d1", source_path="s", markdown_path="m", structure_path="st", assets_dir="a", blocks=[DocumentBlock(block_id="b1", type="paragraph")])
    graph = CognitiveGraph.model_validate({"doc_id": "d1", "nodes": [{"node_id": "n1", "type": "Problem", "content": "p", "source_blocks": ["b1"]}], "edges": [{"edge_id": "e1", "source": "n1", "target": "n1", "relation": "supports", "source_blocks": ["b2"], "evidence_blocks": ["b1"], "human_verified": False}]})
    issues = validate_graph_references(graph, doc)
    assert issues
    assert find_unverified_edges(graph) == ["e1"]
