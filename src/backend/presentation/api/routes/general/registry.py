from fastapi import APIRouter

from backend.presentation.api.routes.general.health import router as health_router

general_router = APIRouter(tags=["general"])

for router in [health_router]:
    general_router.include_router(router, tags=["general"])
