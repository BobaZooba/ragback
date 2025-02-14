from pydantic import BaseModel


class RAGConfig(BaseModel):
    template_name: str = "chat_rag.mako"
    num_search_results: int = 3
    relevance_threshold: float = 0.4
