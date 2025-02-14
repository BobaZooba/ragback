from pydantic import BaseModel, SecretStr


class QdrantVectoreStorageConfig(BaseModel):
    host: SecretStr = SecretStr("localhost")
    port: int = 6333
    collection_name: str = "facts"
