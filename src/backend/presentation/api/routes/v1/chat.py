from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from backend.application.use_cases.chat import ChatUseCase
from backend.presentation.api.models.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
@inject
async def chat_endpoint(
    chat_request: ChatRequest,
    chat_use_case: FromDishka[ChatUseCase],
) -> ChatResponse:
    return await chat_use_case(dto=chat_request)
