from pathlib import Path

import yaml
from pydantic import BaseModel


class ParserSettings(BaseModel):
    default: str = "mock"
    adapters: dict[str, dict] = {
        "mock": {},
        "docling": {"python_module": "docling"},
        "marker": {"command": "marker_single", "extra_args": []},
        "mineru": {"command": "magic-pdf", "extra_args": []},
    }


class LLMSettings(BaseModel):
    provider: str = "mock"
    base_url: str = ""
    model: str = "mock-model"
    api_key_env: str = "OPENAI_API_KEY"


class PromptSettings(BaseModel):
    dir: str = "./prompts"


class Settings(BaseModel):
    workspace_dir: str = "./.cuos_workspace"
    parser: ParserSettings = ParserSettings()
    llm: LLMSettings = LLMSettings()
    prompts: PromptSettings = PromptSettings()

    @classmethod
    def from_file(cls, path: Path) -> "Settings":
        if not path.exists():
            return cls()
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls(**data)
