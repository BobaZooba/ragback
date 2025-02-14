import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from backend.infrastructure.configuration.config import get_config
from backend.infrastructure.di import container
from backend.presentation.api.lifespan import lifespan
from backend.presentation.api.routes.registry import main_router

if __name__ == "__main__":
    config = get_config()

    app = FastAPI(
        title=config.api.title,
        version=config.api.version,
        debug=config.is_debug,
        lifespan=lifespan,
    )

    setup_dishka(container, app)

    app.include_router(main_router)

    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        workers=config.api.workers,
        reload=config.is_debug,
    )
