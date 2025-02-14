from qdrant_client import AsyncQdrantClient
from qdrant_client.models import ScoredPoint
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from backend.application.services.vector_storage import VectorStorageP
from backend.application.value_objects.search_result import SearchResult
from backend.domain.entities.fact import Fact
from backend.domain.value_objects.chat_actor import ChatActor


class QdrantVectorStorage(VectorStorageP):
    def __init__(
        self,
        client: AsyncQdrantClient,
        collection_name: str,
    ):
        self._client = client
        self._collection_name = collection_name

    async def find_nearest(
        self,
        query_embedding: list[float],
        num_search_results: int,
    ) -> list[SearchResult]:
        points = await self._query_nearest_points(
            query_embedding=query_embedding,
            limit=num_search_results,
        )

        results = []
        for hit in points:
            payload = hit.payload or {}
            text = payload.get("text")
            if not text:
                continue

            try:
                fact = Fact(
                    owner=ChatActor(payload.get("owner", ChatActor.USER.value)),
                    text=text,
                )
            except (ValueError, TypeError):
                continue

            results.append(
                SearchResult(content=fact, relevance_score=hit.score or 0.0)  # noqa: WPS358
            )

        return results

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def _query_nearest_points(
        self,
        query_embedding: list[float],
        limit: int,
    ) -> list[ScoredPoint]:
        response = await self._client.query_points(
            collection_name=self._collection_name,
            query=query_embedding,
            limit=limit,
            with_payload=True,
        )
        return response.points
