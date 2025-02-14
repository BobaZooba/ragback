from pydantic import BaseModel


class Character(BaseModel):
    name: str
    age: int
    description: str
