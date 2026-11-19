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
from app.security import encrypt_secret

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


def authorization_response_url(
    redirect_uri: str, params: dict[str, str], *, state: str | None, issuer: str
) -> str:
    """Every redirect back to a client goes through here, so each one carries iss (RFC 9207)."""
    params = dict(params)
    if state is not None:
        params["state"] = state
    params["iss"] = issuer
    sep = "&" if "?" in redirect_uri else "?"
    return f"{redirect_uri}{sep}{urlencode(params)}"


async def _pending_request(
    session: AsyncSession, request_id: str, now: datetime
) -> AuthorizationRequest:
    # Row lock: approve and deny on one request must not both pass the consumed check.
    req: AuthorizationRequest | None = (
        await session.execute(
            select(AuthorizationRequest)
            .where(AuthorizationRequest.request_id_hash == _hash(request_id))
            .with_for_update()
        )
    ).scalar_one_or_none()

    if req is None:
        raise IssueCodeError("invalid_request", "request_id not found", status_code=404)
    if req.consumed_at is not None:
        raise IssueCodeError("invalid_request", "request already consumed")
    if req.expires_at <= now:
        raise IssueCodeError("invalid_request", "request expired")
    return req


async def deny_request(session: AsyncSession, *, issuer: str, request_id: str) -> str:
    """Consume the request so a denied consent page cannot be approved later."""
    req = await _pending_request(session, request_id, datetime.now(UTC))
    req.consumed_at = datetime.now(UTC)
    log.info("authorization_request_denied", client_id=req.client_id)
    return authorization_response_url(
        req.redirect_uri,
        {"error": "access_denied", "error_description": "user denied consent"},
        state=req.state,
        issuer=issuer,
    )


async def issue_code(
    session: AsyncSession,
    *,
    issuer: str,
    request_id: str,
    odoo_user_id: int,
    odoo_api_key_id: int,
    odoo_api_key_value: str | None,
    approved_scope: str,
) -> IssuedCode:
    now = datetime.now(UTC)
    req = await _pending_request(session, request_id, now)

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
    encrypted_api_key = encrypt_secret(odoo_api_key_value) if odoo_api_key_value else None
    auth_code = AuthorizationCode(
        code_hash=_hash(code),
        client_id=req.client_id,
        odoo_user_id=odoo_user_id,
        odoo_api_key_id=odoo_api_key_id,
        odoo_api_key_value=encrypted_api_key,
        redirect_uri=req.redirect_uri,
        scope=" ".join(approved),
        code_challenge=req.code_challenge,
        code_challenge_method=req.code_challenge_method,
        resource=req.resource,
        expires_at=now + CODE_TTL,
    )
    session.add(auth_code)
    req.consumed_at = now

    redirect_to = authorization_response_url(
        req.redirect_uri, {"code": code}, state=req.state, issuer=issuer
    )

    log.info(
        "authorization_code_issued",
        client_id=req.client_id,
        odoo_user_id=odoo_user_id,
        odoo_api_key_id=odoo_api_key_id,
        scopes=approved,
    )
    return IssuedCode(code=code, redirect_to=redirect_to)
