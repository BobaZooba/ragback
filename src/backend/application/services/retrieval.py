import structlog

from backend.application.services.embedder import EmbedderP
from backend.application.services.vector_storage import VectorStorageP
from backend.application.value_objects.search_result import SearchResult

logger = structlog.get_logger()


class RetrievalService:
    def __init__(
        self,
        embedder: EmbedderP,
        vector_storage: VectorStorageP,
        num_search_results: int = 3,
        relevance_threshold: float = 0.85,
    ):
        self._embedder = embedder
        self._vector_storage = vector_storage
        self._num_search_results = num_search_results
        self._relevance_threshold = relevance_threshold

    async def retrieve(self, query: str) -> list[SearchResult]:
        query_embedding = await self._embedder.embed(query=query)
        search_results = await self._vector_storage.find_nearest(
            query_embedding=query_embedding,
            num_search_results=self._num_search_results,
        )
        logger.info(
            "Retrieve results",
            query=query,
            search_results=search_results,
            relevance_threshold=self._relevance_threshold,
        )
        return await self._filter_results(search_results=search_results)

    async def _filter_results(self, search_results: list[SearchResult]) -> list[SearchResult]:
        return list(
            filter(
                lambda result: result.relevance_score >= self._relevance_threshold, search_results
            )
        )
