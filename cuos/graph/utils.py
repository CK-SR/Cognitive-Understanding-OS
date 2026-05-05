from cuos.schemas.document import ParsedDocument
from cuos.schemas.graph import CognitiveGraph, CognitiveNode


def validate_graph_references(
    graph: CognitiveGraph, parsed_doc: ParsedDocument
) -> list[str]:
    block_ids = {b.block_id for b in parsed_doc.blocks}
    issues: list[str] = []
    for node in graph.nodes:
        for b in node.source_blocks:
            if b not in block_ids:
                issues.append(f"node {node.node_id} references missing block {b}")
    for edge in graph.edges:
        for b in edge.source_blocks + edge.evidence_blocks:
            if b not in block_ids:
                issues.append(f"edge {edge.edge_id} references missing block {b}")
    return issues


def find_unverified_edges(graph: CognitiveGraph) -> list[str]:
    return [e.edge_id for e in graph.edges if not e.human_verified]


def find_nodes_by_level(graph: CognitiveGraph, level: str) -> list[CognitiveNode]:
    return [n for n in graph.nodes if n.understanding_level == level]


def export_graph_summary_md(graph: CognitiveGraph) -> str:
    return f"# Candidate Graph\n\n- Nodes: {len(graph.nodes)}\n- Edges: {len(graph.edges)}\n"
