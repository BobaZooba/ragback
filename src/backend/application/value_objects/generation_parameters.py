from pydantic import BaseModel


class GenerationParameters(BaseModel):
    model_name: str
    max_tokens: int = 512
    top_p: float | None = None
    stop: str = "\n"
