def simple_score(answer: str) -> float:
    return min(1.0, len(answer.strip()) / 100)
