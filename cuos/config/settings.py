from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ParserSettings(BaseModel):
    default: str = "mock"
    adapters: dict[str, dict] = Field(
        default_factory=lambda: {
            "mock": {},
            "docling": {"python_module": "docling"},
            "marker": {"command": "marker_single", "extra_args": []},
            "mineru": {"command": "magic-pdf", "extra_args": []},
        }
    )


class LLMSettings(BaseModel):
    provider: str = "mock"
    base_url: str = ""
    model: str = "mock-model"
    api_key_env: str = "DASHSCOPE_API_KEY"
    enable_thinking: bool = False
    timeout: int = 120


class PromptSettings(BaseModel):
    dir: str = "./prompts"


class MapSettings(BaseModel):
    # V1 uses characters rather than tokens. 120k chars is still below the
    # practical context budget of long-context models, while avoiding the old
    # 12k-char truncation that dropped methods/experiments.
    max_input_chars: int = 120000


class LanguageSettings(BaseModel):
    # Source PDFs may be English, but the user interaction and cognitive audit
    # should default to Chinese.
    interaction_language: str = "zh-CN"


class Settings(BaseModel):
    workspace_dir: str = "./.cuos_workspace"
    parser: ParserSettings = Field(default_factory=ParserSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    prompts: PromptSettings = Field(default_factory=PromptSettings)
    map: MapSettings = Field(default_factory=MapSettings)
    language: LanguageSettings = Field(default_factory=LanguageSettings)

    @classmethod
    def from_file(cls, path: Path) -> "Settings":
        if not path.exists():
            return cls()
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls(**data)
