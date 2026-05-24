from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import Settings, get_settings
from app.dependencies import get_session_factory
from app.services.authorize import (
    AuthorizeError,
    AuthorizeParams,
    begin_authorization,
)

router = APIRouter(tags=["oauth"])


def _error_redirect(redirect_uri: str, code: str, description: str, state: str | None) -> str:
    params = {"error": code, "error_description": description}
    if state is not None:
        params["state"] = state
    sep = "&" if "?" in redirect_uri else "?"
    return f"{redirect_uri}{sep}{urlencode(params)}"


@router.get("/authorize", response_model=None)
async def authorize(
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
    settings: Annotated[Settings, Depends(get_settings)],
    client_id: Annotated[str, Query()],
    redirect_uri: Annotated[str, Query()],
    response_type: Annotated[str, Query()],
    code_challenge: Annotated[str, Query()],
    code_challenge_method: Annotated[str, Query()],
    scope: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
    resource: Annotated[str | None, Query()] = None,
) -> RedirectResponse | JSONResponse:
    params = AuthorizeParams(
        client_id=client_id,
        redirect_uri=redirect_uri,
        response_type=response_type,
        scope=scope or "",
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        resource=resource,
    )

    try:
        async with factory() as session:
            issued = await begin_authorization(
                session, params, dashboard_base_url=settings.dashboard_base_url
            )
            await session.commit()
    except AuthorizeError as exc:
        if exc.redirectable:
            return RedirectResponse(
                _error_redirect(redirect_uri, exc.code, exc.description, state),
                status_code=status.HTTP_302_FOUND,
            )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": exc.code, "error_description": exc.description},
        )

    return RedirectResponse(issued.consent_url, status_code=status.HTTP_302_FOUND)
