from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel


class LLMOutputValidationError(ValueError):
    """Raised when LLM output cannot be validated against target schema."""


class LLMClient(Protocol):
    def chat_text(self, messages: list[dict], **kwargs: object) -> str: ...

    def chat_json(
        self, messages: list[dict], schema_model: type[BaseModel], **kwargs: object
    ) -> BaseModel: ...
