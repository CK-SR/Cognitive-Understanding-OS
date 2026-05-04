from cuos.schemas.graph import CognitiveGraph


def build_graph(payload: dict) -> CognitiveGraph:
    return CognitiveGraph.model_validate(payload)
