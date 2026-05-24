"""Pending authorization-request handling for the OAuth front-channel.

`GET /authorize` lands here. We validate the request against the registered
client, persist a single-use, hashed `request_id`, and the route hands the
plaintext id to the dashboard via the consent-screen redirect.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuthorizationRequest, OAuthClient
from app.scopes import DEFAULT_SCOPE, parse_scope, unknown_scopes

log = structlog.get_logger()

REQUEST_TTL: Final = timedelta(minutes=10)
PKCE_MIN_LEN: Final = 43
PKCE_MAX_LEN: Final = 128


class AuthorizeError(Exception):
    """Base for /authorize validation failures.

    `redirectable` distinguishes errors that may be reported by 302 back to
    the client (OAuth 2.1 §4.1.2.1) from those that must NOT redirect
    because the client/redirect_uri couldn't be authenticated.
    """

    def __init__(self, code: str, description: str, *, redirectable: bool) -> None:
        super().__init__(description)
        self.code = code
        self.description = description
        self.redirectable = redirectable


@dataclass(frozen=True)
class AuthorizeParams:
    client_id: str
    redirect_uri: str
    response_type: str
    scope: str
    state: str | None
    code_challenge: str
    code_challenge_method: str
    resource: str | None


@dataclass(frozen=True)
class IssuedRequest:
    request_id: str
    consent_url: str


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _generate_request_id() -> str:
    return secrets.token_urlsafe(32)


async def begin_authorization(
    session: AsyncSession,
    params: AuthorizeParams,
    *,
    dashboard_base_url: str,
) -> IssuedRequest:
    client = (
        await session.execute(
            select(OAuthClient).where(OAuthClient.client_id == params.client_id)
        )
    ).scalar_one_or_none()

    if client is None:
        raise AuthorizeError(
            "invalid_client",
            "unknown client_id",
            redirectable=False,
        )

    if params.redirect_uri not in client.redirect_uris:
        raise AuthorizeError(
            "invalid_request",
            "redirect_uri does not match a registered value",
            redirectable=False,
        )

    if params.response_type != "code":
        raise AuthorizeError(
            "unsupported_response_type",
            "only 'code' is supported",
            redirectable=True,
        )

    if params.code_challenge_method != "S256":
        raise AuthorizeError(
            "invalid_request",
            "code_challenge_method must be 'S256'",
            redirectable=True,
        )
    if not (PKCE_MIN_LEN <= len(params.code_challenge) <= PKCE_MAX_LEN):
        raise AuthorizeError(
            "invalid_request",
            "code_challenge must be 43-128 characters",
            redirectable=True,
        )

    requested_scopes = parse_scope(params.scope) or [DEFAULT_SCOPE]
    bad = unknown_scopes(requested_scopes)
    if bad:
        raise AuthorizeError(
            "invalid_scope",
            f"unknown scope: {bad[0]}",
            redirectable=True,
        )

    request_id = _generate_request_id()
    now = datetime.now(UTC)
    row = AuthorizationRequest(
        request_id_hash=_hash(request_id),
        client_id=client.client_id,
        redirect_uri=params.redirect_uri,
        scope=" ".join(requested_scopes),
        state=params.state,
        code_challenge=params.code_challenge,
        code_challenge_method=params.code_challenge_method,
        resource=params.resource,
        expires_at=now + REQUEST_TTL,
    )
    session.add(row)
    log.info(
        "authorization_request_created",
        client_id=client.client_id,
        scopes=requested_scopes,
        has_state=params.state is not None,
        has_resource=params.resource is not None,
    )

    consent_url = f"{dashboard_base_url.rstrip('/')}/oauth/consent?request_id={request_id}"
    return IssuedRequest(request_id=request_id, consent_url=consent_url)
