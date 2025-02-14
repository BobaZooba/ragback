from pydantic import BaseModel, SecretStr


class CohereEmbedderConfig(BaseModel):
    api_key: SecretStr = SecretStr("cohere_api_key")
    model: str = "embed-english-v3.0"
    input_type: str = "search_query"
    embedding_type: str = "float"
