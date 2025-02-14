from pydantic import BaseModel

from backend.domain.value_objects.chat_actor import ChatActor


class Message(BaseModel):
    actor: ChatActor
    text: str
