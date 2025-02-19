from functools import lru_cache

from pydantic_settings import BaseSettings

from backend.infrastructure.configuration.enums import Environment
from backend.infrastructure.configuration.inner.api import ApiConfig
from backend.infrastructure.configuration.inner.embedder import CohereEmbedderConfig
from backend.infrastructure.configuration.inner.llm import OpenRouterChatLLMConfig
from backend.infrastructure.configuration.inner.rag import RAGConfig
from backend.infrastructure.configuration.inner.vector_storage import QdrantVectoreStorageConfig


class Config(BaseSettings):
    environment: Environment = Environment.DEVELOPMENT

    template_dir: str = "./static/templates/"

    api: ApiConfig = ApiConfig()
    embedder: CohereEmbedderConfig = CohereEmbedderConfig()
    vector_storage: QdrantVectoreStorageConfig = QdrantVectoreStorageConfig()
    chat_llm: OpenRouterChatLLMConfig = OpenRouterChatLLMConfig()
    rag: RAGConfig = RAGConfig()

    @property
    def is_debug(self) -> bool:
        return self.environment == Environment.DEVELOPMENT and self.api.workers is None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "APP__"
        env_nested_delimiter = "__"


@lru_cache
def get_config() -> Config:
    return Config()
