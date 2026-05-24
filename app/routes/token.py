from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.dependencies import get_session_factory
from app.services.token import TokenError, exchange_authorization_code

router = APIRouter(tags=["oauth"])


@router.post("/token")
async def token(
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
    grant_type: Annotated[str, Form()],
    code: Annotated[str | None, Form()] = None,
    redirect_uri: Annotated[str | None, Form()] = None,
    code_verifier: Annotated[str | None, Form()] = None,
    client_id: Annotated[str | None, Form()] = None,
    client_secret: Annotated[str | None, Form()] = None,
) -> dict[str, object]:
    if grant_type != "authorization_code":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "unsupported_grant_type",
                "error_description": "only authorization_code is supported in this slice",
            },
        )
    missing = [
        name
        for name, val in (
            ("client_id", client_id),
            ("code", code),
            ("redirect_uri", redirect_uri),
            ("code_verifier", code_verifier),
        )
        if not val
    ]
    if missing:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_request",
                "error_description": f"missing required form fields: {', '.join(missing)}",
            },
        )

    assert client_id is not None and code is not None
    assert redirect_uri is not None and code_verifier is not None

    try:
        async with factory() as session:
            tokens = await exchange_authorization_code(
                session,
                client_id=client_id,
                client_secret=client_secret,
                code=code,
                redirect_uri=redirect_uri,
                code_verifier=code_verifier,
            )
            await session.commit()
    except TokenError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"error": exc.code, "error_description": exc.description},
        ) from exc

    return {
        "access_token": tokens.access_token,
        "token_type": "Bearer",
        "expires_in": tokens.expires_in,
        "refresh_token": tokens.refresh_token,
        "scope": tokens.scope,
    }
