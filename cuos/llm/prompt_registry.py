from __future__ import annotations

from pathlib import Path


class PromptRegistry:
    def __init__(self, prompt_dir: Path) -> None:
        self.prompt_dir = prompt_dir

    def load(self, name: str, variables: dict[str, str] | None = None) -> str:
        path = self.prompt_dir / name
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        template = path.read_text(encoding="utf-8")
        variables = variables or {}
        for key, value in variables.items():
            template = template.replace(f"{{{{{key}}}}}", value)
        return template
