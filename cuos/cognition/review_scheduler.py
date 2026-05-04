from datetime import date


def due_today() -> str:
    return date.today().isoformat()
