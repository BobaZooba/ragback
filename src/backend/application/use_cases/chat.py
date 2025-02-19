from structlog import get_logger

from backend.application.services.llm import LLMServiceP
from backend.application.services.prompt import PromptBuilderServiceP
from backend.application.services.retrieval import RetrievalService
from backend.application.value_objects.prompts_data.rag import RAGPromptData
from backend.application.value_objects.search_result import SearchResult
from backend.domain.entities.message import Message
from backend.presentation.api.models.chat import ChatRequest, ChatResponse

logger = get_logger()


class ChatUseCase:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_prompt_builder_service: PromptBuilderServiceP[RAGPromptData],
        llm_service: LLMServiceP,
    ):
        self._retrieval_service = retrieval_service
        self._llm_prompt_builder_service = llm_prompt_builder_service
        self._llm_service = llm_service

    async def __call__(self, dto: ChatRequest) -> ChatResponse:
        search_results = await self._retrieve_and_filter(messages=dto.messages)

        prompt_data = RAGPromptData(
            user=dto.user,
            character=dto.character,
            messages=dto.messages,
            search_results=search_results,
        )

        llm_prompt = await self._llm_prompt_builder_service.make(prompt_data=prompt_data)

        character_generated_message_text = await self._llm_service.generate(prompt=llm_prompt)

        return ChatResponse(
            generated_text=character_generated_message_text,
            search_results=search_results,
        )

    async def _retrieve_and_filter(self, messages: list[Message]) -> list[SearchResult]:
        search_results: list[SearchResult] = []

        if messages:
            try:
                search_results = await self._retrieval_service.retrieve(
                    query=messages[-1].text,
                )
            except Exception as exception:
                logger.exception("Retrieval service exception", exception=str(exception))

        return search_results
