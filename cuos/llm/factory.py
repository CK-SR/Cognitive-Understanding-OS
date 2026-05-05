from cuos.config.settings import LLMSettings
from cuos.llm.base import LLMClient
from cuos.llm.mock_client import MockLLMClient
from cuos.llm.openai_compatible import OpenAICompatibleLLMClient


def get_llm_client(settings: LLMSettings) -> LLMClient:
    if settings.provider == "mock":
        return MockLLMClient()
    if settings.provider == "openai-compatible":
        return OpenAICompatibleLLMClient(
            base_url=settings.base_url,
            model=settings.model,
            api_key_env=settings.api_key_env,
            enable_thinking=settings.enable_thinking,
            timeout=settings.timeout,
        )
    raise ValueError(f"Unsupported llm provider: {settings.provider}")
