from pydantic import BaseModel


class ApiConfig(BaseModel):
    title: str = "RAG Chat API"
    version: str = "0.0.1"
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int | None = None
