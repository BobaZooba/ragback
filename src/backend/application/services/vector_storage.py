from typing import Protocol

from backend.application.value_objects.search_result import SearchResult


class VectorStorageP(Protocol):
    async def find_nearest(
        self,
        query_embedding: list[float],
        num_search_results: int,
    ) -> list[SearchResult]: ...
