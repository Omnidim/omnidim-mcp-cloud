from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.dependencies import get_session_factory

router = APIRouter(tags=["health"])

log = structlog.get_logger()


@router.get("/healthz", include_in_schema=False)
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz", include_in_schema=False)
async def readiness(
    response: Response,
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
) -> dict[str, str]:
    try:
        async with factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        log.warning("readiness_db_failed", exc_info=True)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "degraded", "database": "unreachable"}
    return {"status": "ok"}
