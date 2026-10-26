from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1.router import router as v1_router
from core.config import settings
from core.exceptions import register_exception_handlers
from middleware.logging import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(LoggingMiddleware)
    app.include_router(v1_router, prefix="/api/v1")
    register_exception_handlers(app)
    return app


app = create_app()
