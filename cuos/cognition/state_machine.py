def next_state(current: str) -> str:
    return "reflect" if current == "answer" else "answer"
