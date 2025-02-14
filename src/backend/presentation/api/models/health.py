from pydantic import BaseModel

from backend.infrastructure.configuration.enums import Environment


class HealthResponse(BaseModel):
    is_healthy: bool = True
    environment: Environment
