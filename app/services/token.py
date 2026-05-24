"""Auth code → access + refresh exchange.

PKCE S256 verification, single-use code enforcement, refresh token rotation.
Access + refresh tokens are persisted as SHA-256 hashes; plaintext is
returned to the client exactly once in the /token response.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Final

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AccessToken, AuthorizationCode, OAuthClient, RefreshToken
from app.services.clients import hash_secret

log = structlog.get_logger()

ACCESS_TOKEN_TTL: Final = timedelta(seconds=3600)
REFRESH_TOKEN_TTL: Final = timedelta(days=90)


class TokenError(Exception):
    def __init__(self, code: str, description: str, status_code: int = 400) -> None:
        super().__init__(description)
        self.code = code
        self.description = description
        self.status_code = status_code


@dataclass(frozen=True)
class IssuedTokens:
    access_token: str
    refresh_token: str
    expires_in: int
    scope: str


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _generate_token() -> str:
    return secrets.token_urlsafe(48)


def _generate_grant_id() -> str:
    return secrets.token_urlsafe(16)


def _verify_pkce(verifier: str, expected_challenge: str) -> bool:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return hmac.compare_digest(computed, expected_challenge)


async def _authenticate_client(
    session: AsyncSession, client_id: str, client_secret: str | None
) -> OAuthClient:
    client: OAuthClient | None = (
        await session.execute(select(OAuthClient).where(OAuthClient.client_id == client_id))
    ).scalar_one_or_none()
    if client is None:
        raise TokenError("invalid_client", "unknown client_id", status_code=401)
    if client.token_endpoint_auth_method == "none":  # noqa: S105
        if client_secret is not None:
            raise TokenError("invalid_client", "public client must not present a secret", 401)
        return client
    if client_secret is None:
        raise TokenError("invalid_client", "client authentication required", 401)
    if client.client_secret_hash is None:
        raise TokenError("invalid_client", "client has no secret on file", 401)
    if not hmac.compare_digest(hash_secret(client_secret), client.client_secret_hash):
        raise TokenError("invalid_client", "bad client_secret", 401)
    return client


async def exchange_authorization_code(
    session: AsyncSession,
    *,
    client_id: str,
    client_secret: str | None,
    code: str,
    redirect_uri: str,
    code_verifier: str,
) -> IssuedTokens:
    client = await _authenticate_client(session, client_id, client_secret)

    now = datetime.now(UTC)
    auth_code: AuthorizationCode | None = (
        await session.execute(
            select(AuthorizationCode).where(AuthorizationCode.code_hash == _hash(code))
        )
    ).scalar_one_or_none()

    if auth_code is None:
        raise TokenError("invalid_grant", "code not found")
    if auth_code.client_id != client.client_id:
        raise TokenError("invalid_grant", "code does not belong to this client")
    if auth_code.consumed_at is not None:
        raise TokenError("invalid_grant", "code already used")
    if auth_code.expires_at <= now:
        raise TokenError("invalid_grant", "code expired")
    if auth_code.redirect_uri != redirect_uri:
        raise TokenError("invalid_grant", "redirect_uri mismatch")
    if not _verify_pkce(code_verifier, auth_code.code_challenge):
        raise TokenError("invalid_grant", "PKCE verifier does not match challenge")

    auth_code.consumed_at = now

    access_plain = _generate_token()
    refresh_plain = _generate_token()
    grant_id = _generate_grant_id()

    session.add(
        AccessToken(
            token_hash=_hash(access_plain),
            client_id=client.client_id,
            odoo_user_id=auth_code.odoo_user_id,
            odoo_api_key_id=auth_code.odoo_api_key_id,
            grant_id=grant_id,
            scope=auth_code.scope,
            expires_at=now + ACCESS_TOKEN_TTL,
        )
    )
    session.add(
        RefreshToken(
            token_hash=_hash(refresh_plain),
            client_id=client.client_id,
            odoo_user_id=auth_code.odoo_user_id,
            grant_id=grant_id,
            scope=auth_code.scope,
            expires_at=now + REFRESH_TOKEN_TTL,
        )
    )

    log.info(
        "tokens_issued",
        client_id=client.client_id,
        odoo_user_id=auth_code.odoo_user_id,
        grant_id=grant_id,
    )

    return IssuedTokens(
        access_token=access_plain,
        refresh_token=refresh_plain,
        expires_in=int(ACCESS_TOKEN_TTL.total_seconds()),
        scope=auth_code.scope,
    )
