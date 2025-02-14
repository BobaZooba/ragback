from typing import Protocol

from backend.application.value_objects.generation_parameters import GenerationParameters


class LLMServiceP(Protocol):
    _generation_parameters: GenerationParameters

    async def generate(self, prompt: str) -> str: ...
