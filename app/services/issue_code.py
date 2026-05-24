"""Consume a pending authorization request and mint an auth code.

Called by the dashboard server-side after the user clicks Allow. Bridges the
pre-consent `oauth_authorization_request` row to the post-consent
`oauth_authorization_code` row, carrying the PKCE challenge + redirect_uri +
scope (filtered to what the user approved) + the Odoo api-key id that was
just minted on the user's behalf.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final
from urllib.parse import urlencode

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuthorizationCode, AuthorizationRequest
from app.scopes import parse_scope, unknown_scopes

log = structlog.get_logger()

CODE_TTL: Final = timedelta(minutes=2)


class IssueCodeError(Exception):
    def __init__(self, code: str, description: str, status_code: int = 400) -> None:
        super().__init__(description)
        self.code = code
        self.description = description
        self.status_code = status_code


@dataclass(frozen=True)
class IssuedCode:
    code: str
    redirect_to: str


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _generate_code() -> str:
    return secrets.token_urlsafe(32)


async def issue_code(
    session: AsyncSession,
    *,
    request_id: str,
    odoo_user_id: int,
    odoo_api_key_id: int,
    approved_scope: str,
) -> IssuedCode:
    now = datetime.now(UTC)
    req: AuthorizationRequest | None = (
        await session.execute(
            select(AuthorizationRequest).where(
                AuthorizationRequest.request_id_hash == _hash(request_id)
            )
        )
    ).scalar_one_or_none()

    if req is None:
        raise IssueCodeError("invalid_request", "request_id not found", status_code=404)
    if req.consumed_at is not None:
        raise IssueCodeError("invalid_request", "request already consumed")
    if req.expires_at <= now:
        raise IssueCodeError("invalid_request", "request expired")

    requested = parse_scope(req.scope)
    approved = parse_scope(approved_scope)
    if not approved:
        raise IssueCodeError("invalid_scope", "approved_scope cannot be empty")
    bad = [s for s in approved if s not in requested]
    if bad:
        raise IssueCodeError("invalid_scope", f"approved scope not in original request: {bad[0]}")
    unknown = unknown_scopes(approved)
    if unknown:
        raise IssueCodeError("invalid_scope", f"unknown scope: {unknown[0]}")

    code = _generate_code()
    auth_code = AuthorizationCode(
        code_hash=_hash(code),
        client_id=req.client_id,
        odoo_user_id=odoo_user_id,
        odoo_api_key_id=odoo_api_key_id,
        redirect_uri=req.redirect_uri,
        scope=" ".join(approved),
        code_challenge=req.code_challenge,
        code_challenge_method=req.code_challenge_method,
        resource=req.resource,
        expires_at=now + CODE_TTL,
    )
    session.add(auth_code)
    req.consumed_at = now

    params = {"code": code}
    if req.state is not None:
        params["state"] = req.state
    sep = "&" if "?" in req.redirect_uri else "?"
    redirect_to = f"{req.redirect_uri}{sep}{urlencode(params)}"

    log.info(
        "authorization_code_issued",
        client_id=req.client_id,
        odoo_user_id=odoo_user_id,
        odoo_api_key_id=odoo_api_key_id,
        scopes=approved,
    )
    return IssuedCode(code=code, redirect_to=redirect_to)
