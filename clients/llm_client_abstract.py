from abc import ABC, abstractmethod


class LLMClient(ABC):
    @abstractmethod
    def generate(
        self, prompt: str, system_prompt: str = None, model: str = "mock"
    ) -> str:
        pass
