from __future__ import annotations

import json
import os
import time
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
    def __init__(
        self,
        base_url: str,
        model: str,
        api_key_env: str = "DASHSCOPE_API_KEY",
        enable_thinking: bool = False,
        timeout: int = 120,
    ) -> None:
        api_key = os.getenv(api_key_env, "")
        if not api_key:
            raise ValueError(
                f"API key not found in environment variable '{api_key_env}'. "
                f"Set it with: export {api_key_env}='sk-xxx'"
            )
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai package is not installed. Install with: pip install 'cuos[openai]' or pip install openai>=1.0"
            ) from exc

        self.client = OpenAI(
            base_url=base_url or None, api_key=api_key, timeout=timeout
        )
        self.model = model
        self.enable_thinking = enable_thinking

    def _build_extra_body(self) -> dict[str, Any]:
        if self.enable_thinking:
            return {"enable_thinking": True}
        return {}

    def chat_text(self, messages: list[dict], **kwargs: object) -> str:
        extra_body = self._build_extra_body()
        api_kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "extra_body": extra_body,
        }
        api_kwargs.update(kwargs)
        response = self.client.chat.completions.create(**api_kwargs)
        return response.choices[0].message.content or ""

    def chat_json(
        self, messages: list[dict], schema_model: type[BaseModel], **kwargs: object
    ) -> BaseModel:
        t0 = time.monotonic()
        try:
            text = self.chat_text(messages, **kwargs)
            latency_ms = int((time.monotonic() - t0) * 1000)
            parsed = extract_json_object(text)
            result = schema_model.model_validate(parsed)
            _log_llm_call(self.model, latency_ms, parse_success=True)
            return result
        except (json.JSONDecodeError, ValidationError) as first_error:
            latency_ms = int((time.monotonic() - t0) * 1000)
            _log_llm_call(self.model, latency_ms, parse_success=False)
            repair_messages = messages + [
                {"role": "assistant", "content": text},
                {
                    "role": "user",
                    "content": f"Your output failed validation: {first_error}. Return JSON only and follow schema exactly.",
                },
            ]
            t1 = time.monotonic()
            try:
                repaired = self.chat_text(repair_messages, **kwargs)
                latency_ms2 = int((time.monotonic() - t1) * 1000)
                result = schema_model.model_validate(extract_json_object(repaired))
                _log_llm_call(self.model, latency_ms2, parse_success=True, retry=True)
                return result
            except Exception as second_error:
                _log_llm_call(self.model, latency_ms2, parse_success=False, retry=True)
                raise LLMOutputValidationError(
                    f"Failed to validate LLM output: {second_error}"
                ) from second_error


def _log_llm_call(
    model: str, latency_ms: int, parse_success: bool, retry: bool = False
) -> None:
    import logging

    logger = logging.getLogger("cuos.llm")
    logger.info(
        "llm_call",
        extra={
            "event": "llm_call",
            "model_name": model,
            "latency_ms": latency_ms,
            "parse_success": parse_success,
            "retry": retry,
        },
    )
