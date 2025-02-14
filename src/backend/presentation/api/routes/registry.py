from fastapi import APIRouter

from backend.presentation.api.routes.general.registry import general_router
from backend.presentation.api.routes.v1.registry import v1_router

main_router = APIRouter()

for router in [general_router, v1_router]:
    main_router.include_router(router)
