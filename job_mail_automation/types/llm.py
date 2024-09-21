from abc import ABC

from .prompt import LLMPrompt


class LLMService(ABC):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        return f"LLM: {self.kwargs}"

    def run(self, messages: LLMPrompt) -> str | None:
        raise NotImplementedError
