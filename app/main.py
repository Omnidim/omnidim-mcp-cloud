from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.config import get_settings
from app.db import build_engine, build_session_factory
from app.errors import install_oauth_error_handler
from app.logging import configure_logging
from app.middleware import RequestIdMiddleware
from app.routes import authorize, health, internal, mcp, register, telemetry, token, wellknown


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    log = structlog.get_logger()

    engine = build_engine(settings)
    app.state.engine = engine
    app.state.session_factory = build_session_factory(engine)
    log.info("startup", environment=settings.environment)
    try:
        yield
    finally:
        await engine.dispose()
        log.info("shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="OmniDimension MCP",
        version="0.0.1",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.add_middleware(RequestIdMiddleware)
    install_oauth_error_handler(app)
    app.include_router(health.router)
    app.include_router(wellknown.router)
    app.include_router(register.router)
    app.include_router(authorize.router)
    app.include_router(internal.router)
    app.include_router(token.router)
    app.include_router(mcp.router)
    app.include_router(telemetry.router)
    return app


app = create_app()
