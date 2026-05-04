from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def generate_json(self, task_type: str, prompt_id: str, variables: dict) -> dict:
        raise NotImplementedError
