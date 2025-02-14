from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter

from backend.infrastructure.configuration.config import Config
from backend.presentation.api.models.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
@inject
async def health_endpoint(config: FromDishka[Config]) -> HealthResponse:
    return HealthResponse(environment=config.environment)
