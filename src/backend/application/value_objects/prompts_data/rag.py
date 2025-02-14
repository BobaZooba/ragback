from pydantic import BaseModel

from backend.application.value_objects.search_result import SearchResult
from backend.domain.entities.character import Character
from backend.domain.entities.message import Message
from backend.domain.entities.user import User


class RAGPromptData(BaseModel):
    user: User
    character: Character
    messages: list[Message]
    search_results: list[SearchResult]
