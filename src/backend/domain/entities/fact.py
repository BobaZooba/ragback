from pydantic import BaseModel

from backend.domain.value_objects.chat_actor import ChatActor


class Fact(BaseModel):
    owner: ChatActor
    text: str
