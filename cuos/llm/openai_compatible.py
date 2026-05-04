from __future__ import annotations

import json
import os
from typing import Any

from pydantic import BaseModel, ValidationError

from cuos.llm.base import LLMClient, LLMOutputValidationError


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        stripped = stripped.replace("json\n", "", 1)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


class OpenAICompatibleLLMClient(LLMClient):
    def __init__(self, base_url: str, model: str, api_key_env: str = "CUOS_LLM_API_KEY") -> None:
        api_key = os.getenv(api_key_env, "")
        from openai import OpenAI

        self.client = OpenAI(base_url=base_url or None, api_key=api_key)
        self.model = model

    def chat_text(self, messages: list[dict], **kwargs: object) -> str:
        response = self.client.chat.completions.create(model=self.model, messages=messages, **kwargs)
        return response.choices[0].message.content or ""

    def chat_json(self, messages: list[dict], schema_model: type[BaseModel], **kwargs: object) -> BaseModel:
        try:
            text = self.chat_text(messages, **kwargs)
            return schema_model.model_validate(extract_json_object(text))
        except (json.JSONDecodeError, ValidationError) as first_error:
            repair_messages = messages + [
                {"role": "assistant", "content": text},
                {
                    "role": "user",
                    "content": f"Your output failed validation: {first_error}. Return JSON only and follow schema exactly.",
                },
            ]
            try:
                repaired = self.chat_text(repair_messages, **kwargs)
                return schema_model.model_validate(extract_json_object(repaired))
            except Exception as second_error:  # noqa: BLE001
                raise LLMOutputValidationError(f"Failed to validate LLM output: {second_error}") from second_error
