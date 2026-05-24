from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.dependencies import get_session_factory
from app.services.token import (
    TokenError,
    exchange_authorization_code,
    exchange_refresh_token,
    revoke,
)

router = APIRouter(tags=["oauth"])


def _raise(exc: TokenError) -> None:
    raise HTTPException(
        status_code=exc.status_code,
        detail={"error": exc.code, "error_description": exc.description},
    ) from exc


@router.post("/token")
async def token(
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
    grant_type: Annotated[str, Form()],
    code: Annotated[str | None, Form()] = None,
    redirect_uri: Annotated[str | None, Form()] = None,
    code_verifier: Annotated[str | None, Form()] = None,
    refresh_token: Annotated[str | None, Form()] = None,
    client_id: Annotated[str | None, Form()] = None,
    client_secret: Annotated[str | None, Form()] = None,
) -> dict[str, object]:
    if grant_type == "authorization_code":
        missing = [
            n
            for n, v in (
                ("client_id", client_id),
                ("code", code),
                ("redirect_uri", redirect_uri),
                ("code_verifier", code_verifier),
            )
            if not v
        ]
        if missing:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_request",
                    "error_description": f"missing required form fields: {', '.join(missing)}",
                },
            )
        assert client_id and code and redirect_uri and code_verifier
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
            _raise(exc)

    elif grant_type == "refresh_token":
        if not client_id or not refresh_token:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_request",
                    "error_description": "refresh_token grant requires client_id + refresh_token",
                },
            )
        try:
            async with factory() as session:
                tokens = await exchange_refresh_token(
                    session,
                    client_id=client_id,
                    client_secret=client_secret,
                    refresh_token=refresh_token,
                )
                await session.commit()
        except TokenError as exc:
            _raise(exc)

    else:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "unsupported_grant_type",
                "error_description": (
                    "supported: authorization_code, refresh_token"
                ),
            },
        )

    return {
        "access_token": tokens.access_token,
        "token_type": "Bearer",
        "expires_in": tokens.expires_in,
        "refresh_token": tokens.refresh_token,
        "scope": tokens.scope,
    }


@router.post("/revoke")
async def revoke_endpoint(
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
    token: Annotated[str, Form()],
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str | None, Form()] = None,
    # RFC 7009 §2.1 lets the client send a token_type_hint; we don't need
    # it because we look up by hash in both tables anyway.
    token_type_hint: Annotated[str | None, Form()] = None,
) -> Response:
    try:
        async with factory() as session:
            await revoke(session, client_id=client_id, client_secret=client_secret, token=token)
            await session.commit()
    except TokenError as exc:
        _raise(exc)
    # RFC 7009 §2.2: success returns 200 with no body, regardless of whether
    # the token existed (prevents probing).
    return Response(status_code=200)
