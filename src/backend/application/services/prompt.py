from typing import Protocol, TypeVar

from pydantic import BaseModel

PromptDataT = TypeVar("PromptDataT", bound=BaseModel, contravariant=True)


class PromptBuilderServiceP(Protocol[PromptDataT]):
    async def make(self, prompt_data: PromptDataT) -> str: ...
