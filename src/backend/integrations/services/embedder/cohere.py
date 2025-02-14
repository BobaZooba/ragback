from cohere import AsyncClientV2 as CohereClient
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from backend.application.services.embedder import EmbedderP


class CohereEmbedder(EmbedderP):
    def __init__(
        self,
        client: CohereClient,
        model: str = "embed-english-v3.0",
        input_type: str = "search_query",
        embedding_type: str = "float",
    ):
        self._client = client
        self._model = model
        self._input_type = input_type
        self._embedding_type = embedding_type

    async def embed(self, query: str) -> list[float]:
        return await self._make_embedding_request(text=query)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def _make_embedding_request(self, text: str) -> list[float]:
        response = await self._client.embed(
            texts=[text],
            model=self._model,
            input_type=self._input_type,
            embedding_types=[self._embedding_type],
        )
        if response.embeddings.float_ is None:
            raise ValueError("Cohere vector embedding is None")
        return response.embeddings.float_[0]
