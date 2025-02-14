from pydantic import BaseModel, SecretStr

from backend.application.value_objects.generation_parameters import GenerationParameters


class OpenRouterChatLLMConfig(BaseModel):
    api_key: SecretStr = SecretStr("openrouter_api_key")
    base_url: str = "https://openrouter.ai/api/v1"
    generation_parameters: GenerationParameters = GenerationParameters(model_name="openai/gpt-4o")
