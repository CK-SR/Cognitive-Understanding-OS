from cuos.config.settings import LLMSettings
from cuos.llm.base import LLMClient
from cuos.llm.mock_client import MockLLMClient
from cuos.llm.openai_compatible import OpenAICompatibleLLMClient


def get_llm_client(settings: LLMSettings) -> LLMClient:
    if settings.provider == "mock":
        return MockLLMClient()
    if settings.provider == "openai-compatible":
        return OpenAICompatibleLLMClient(settings.base_url, settings.model, settings.api_key_env)
    raise ValueError(f"Unsupported llm provider: {settings.provider}")
