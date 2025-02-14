from cohere import AsyncClientV2 as CohereClient
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import FastapiProvider
from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient

from backend.application.services.embedder import EmbedderP
from backend.application.services.llm import LLMServiceP
from backend.application.services.retrieval import RetrievalService
from backend.application.services.vector_storage import VectorStorageP
from backend.application.use_cases.chat import ChatUseCase
from backend.infrastructure.configuration.config import Config, get_config
from backend.integrations.services.embedder.cohere import CohereEmbedder
from backend.integrations.services.llm.openai import OpenAILikeLLM
from backend.integrations.services.prompts.rag import MakoRAGPromptBuilder
from backend.integrations.services.vector_storage.qdrant import QdrantVectorStorage


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> Config:
        return get_config()


class ClientsProvider(Provider):
    @provide(scope=Scope.APP)
    def get_cohere_client(self, config: Config) -> CohereClient:
        return CohereClient(api_key=config.embedder.api_key.get_secret_value())

    @provide(scope=Scope.APP)
    def get_openai_client(self, config: Config) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=config.chat_llm.api_key.get_secret_value(),
            base_url=config.chat_llm.base_url,
        )

    @provide(scope=Scope.APP)
    def get_qdrant_client(self, config: Config) -> AsyncQdrantClient:
        return AsyncQdrantClient(
            host=config.vector_storage.host.get_secret_value(),
            port=config.vector_storage.port,
        )


class ServicesProvider(Provider):
    @provide(scope=Scope.APP)
    def get_embedder(self, client: CohereClient, config: Config) -> EmbedderP:
        return CohereEmbedder(
            client=client,
            model=config.embedder.model,
            input_type=config.embedder.input_type,
            embedding_type=config.embedder.embedding_type,
        )

    @provide(scope=Scope.APP)
    def get_llm(self, client: AsyncOpenAI, config: Config) -> LLMServiceP:
        return OpenAILikeLLM(
            client=client,
            generation_parameters=config.chat_llm.generation_parameters,
        )

    @provide(scope=Scope.APP)
    def get_vector_storage(
        self,
        client: AsyncQdrantClient,
        config: Config,
    ) -> VectorStorageP:
        return QdrantVectorStorage(
            client=client,
            collection_name=config.vector_storage.collection_name,
        )

    @provide(scope=Scope.APP)
    def get_prompt_builder(
        self,
        config: Config,
    ) -> MakoRAGPromptBuilder:
        return MakoRAGPromptBuilder(
            templates_dir=config.template_dir,
            template_name=config.rag.template_name,
        )


class ApplicationProvider(Provider):
    @provide(scope=Scope.APP)
    def get_retrieval_service(
        self,
        embedder: EmbedderP,
        vector_storage: VectorStorageP,
        config: Config,
    ) -> RetrievalService:
        return RetrievalService(
            embedder=embedder,
            vector_storage=vector_storage,
            num_search_results=config.rag.num_search_results,
            relevance_threshold=config.rag.relevance_threshold,
        )

    @provide(scope=Scope.APP)
    def get_chat_use_case(
        self,
        retrieval_service: RetrievalService,
        prompt_builder: MakoRAGPromptBuilder,
        llm: LLMServiceP,
    ) -> ChatUseCase:
        return ChatUseCase(
            retrieval_service=retrieval_service,
            llm_prompt_builder_service=prompt_builder,
            llm_service=llm,
        )


container = make_async_container(
    ConfigProvider(),
    ClientsProvider(),
    ServicesProvider(),
    ApplicationProvider(),
    FastapiProvider(),
)
