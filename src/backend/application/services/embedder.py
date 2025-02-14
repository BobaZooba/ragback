from typing import Protocol


class EmbedderP(Protocol):
    async def embed(self, query: str) -> list[float]: ...
