from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionUserMessageParam
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from backend.application.services.llm import LLMServiceP
from backend.application.value_objects.generation_parameters import GenerationParameters


class OpenAILikeLLM(LLMServiceP):
    def __init__(
        self,
        client: AsyncOpenAI,
        generation_parameters: GenerationParameters,
    ):
        self._client = client
        self._generation_parameters = generation_parameters

    async def generate(self, prompt: str) -> str:
        message = ChatCompletionUserMessageParam(
            content=prompt,
            role="user",
        )
        return await self._make_completion_request(messages=[message])

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def _make_completion_request(
        self,
        messages: list[ChatCompletionUserMessageParam],
    ) -> str:
        response = await self._client.chat.completions.create(
            messages=messages,
            model=self._generation_parameters.model_name,
            max_tokens=self._generation_parameters.max_tokens,
            top_p=self._generation_parameters.top_p,
            stop=[self._generation_parameters.stop],
        )

        generated_text = response.choices[0].message.content
        if not generated_text:
            raise ValueError(f"Generated text is {generated_text}")
        return generated_text
