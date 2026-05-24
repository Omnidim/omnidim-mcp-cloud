"""Internal endpoints called by the dashboard during the consent flow.

These are not part of the public OAuth surface. They're gated by a shared
secret carried in the `X-Internal-Secret` header. The dashboard fetches
pending request metadata to render the consent screen.
"""
from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import Settings, get_settings
from app.dependencies import get_session_factory
from app.models import AuthorizationRequest, OAuthClient
from app.schemas.oauth import IssueCodeRequest, IssueCodeResponse
from app.services.issue_code import IssueCodeError, issue_code

router = APIRouter(prefix="/internal", tags=["internal"], include_in_schema=False)


def _require_shared_secret(
    settings: Annotated[Settings, Depends(get_settings)],
    x_internal_secret: Annotated[str | None, Header(alias="X-Internal-Secret")] = None,
) -> None:
    expected = settings.odoo_internal_shared_secret
    provided = x_internal_secret or ""
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid secret")


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@router.get(
    "/authorization-request/{request_id}",
    dependencies=[Depends(_require_shared_secret)],
)
async def get_authorization_request(
    request_id: str,
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
) -> dict[str, object]:
    async with factory() as session:
        row: AuthorizationRequest | None = (
            await session.execute(
                select(AuthorizationRequest).where(
                    AuthorizationRequest.request_id_hash == _hash(request_id)
                )
            )
        ).scalar_one_or_none()

        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="request not found"
            )

        now = datetime.now(UTC)
        expired = row.expires_at <= now
        consumed = row.consumed_at is not None

        client: OAuthClient | None = (
            await session.execute(
                select(OAuthClient).where(OAuthClient.client_id == row.client_id)
            )
        ).scalar_one_or_none()

    return {
        "client_id": row.client_id,
        "client_name": client.client_name if client is not None else row.client_id,
        "software_id": client.software_id if client is not None else None,
        "redirect_uri": row.redirect_uri,
        "scope": row.scope,
        "state": row.state,
        "expires_at": row.expires_at.isoformat(),
        "expired": expired,
        "consumed": consumed,
    }


@router.post(
    "/issue-code",
    dependencies=[Depends(_require_shared_secret)],
    response_model=IssueCodeResponse,
)
async def post_issue_code(
    body: IssueCodeRequest,
    factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
) -> IssueCodeResponse:
    try:
        async with factory() as session:
            issued = await issue_code(
                session,
                request_id=body.request_id,
                odoo_user_id=body.odoo_user_id,
                odoo_api_key_id=body.odoo_api_key_id,
                approved_scope=body.approved_scope,
            )
            await session.commit()
    except IssueCodeError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail={"error": exc.code, "error_description": exc.description},
        ) from exc
    return IssueCodeResponse(code=issued.code, redirect_to=issued.redirect_to)
