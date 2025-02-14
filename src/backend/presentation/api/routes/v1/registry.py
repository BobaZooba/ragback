from fastapi import APIRouter

from backend.presentation.api.routes.v1.chat import router as chat_router

v1_router = APIRouter(prefix="/api/v1")

for router in [chat_router]:
    v1_router.include_router(router, tags=["v1"])
