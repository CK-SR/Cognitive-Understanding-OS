from pathlib import Path


class PromptRegistry:
    def __init__(self, prompt_dir: Path) -> None:
        self.prompt_dir = prompt_dir

    def load(self, name: str) -> str:
        return (self.prompt_dir / name).read_text(encoding="utf-8")
