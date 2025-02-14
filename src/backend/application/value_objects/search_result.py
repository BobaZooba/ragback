from pydantic import BaseModel

from backend.domain.entities.fact import Fact


class SearchResult(BaseModel):
    content: Fact
    relevance_score: float
