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
from sqlalchemy import select, update
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


async def exchange_refresh_token(
    session: AsyncSession,
    *,
    client_id: str,
    client_secret: str | None,
    refresh_token: str,
) -> IssuedTokens:
    """OAuth 2.1 refresh-token grant with rotation.

    Consumes the presented refresh token, issues a fresh access + refresh
    pair under the same grant_id. Detects replay: if the consumed token is
    presented again, all tokens under that grant_id are revoked (token-
    family invalidation per RFC 6819 §5.2.2.3).
    """
    client = await _authenticate_client(session, client_id, client_secret)

    now = datetime.now(UTC)
    presented = (
        await session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == _hash(refresh_token))
        )
    ).scalar_one_or_none()

    if presented is None or presented.client_id != client.client_id:
        raise TokenError("invalid_grant", "refresh token not recognised")
    if presented.expires_at <= now:
        raise TokenError("invalid_grant", "refresh token expired")
    if presented.consumed_at is not None:
        # Replay: revoke the whole grant family so a stolen token can't be
        # used past its successor's lifetime.
        await session.execute(
            update(AccessToken)
            .where(AccessToken.grant_id == presented.grant_id)
            .values(revoked_at=now)
        )
        raise TokenError("invalid_grant", "refresh token already used (grant revoked)")

    # Borrow the upstream credential from the original access token in this
    # grant so the new pair stays bound to the same Odoo user.api.key.
    access_row: AccessToken | None = (
        await session.execute(
            select(AccessToken)
            .where(AccessToken.grant_id == presented.grant_id)
            .order_by(AccessToken.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if access_row is None:
        raise TokenError("invalid_grant", "grant has no access token on file")

    new_access = _generate_token()
    new_refresh = _generate_token()

    session.add(
        AccessToken(
            token_hash=_hash(new_access),
            client_id=client.client_id,
            odoo_user_id=presented.odoo_user_id,
            odoo_api_key_id=access_row.odoo_api_key_id,
            odoo_api_key_value=access_row.odoo_api_key_value,
            grant_id=presented.grant_id,
            scope=presented.scope,
            expires_at=now + ACCESS_TOKEN_TTL,
        )
    )
    new_refresh_row = RefreshToken(
        token_hash=_hash(new_refresh),
        client_id=client.client_id,
        odoo_user_id=presented.odoo_user_id,
        grant_id=presented.grant_id,
        scope=presented.scope,
        expires_at=now + REFRESH_TOKEN_TTL,
    )
    session.add(new_refresh_row)
    presented.consumed_at = now
    presented.replaced_by_hash = _hash(new_refresh)

    log.info(
        "tokens_refreshed",
        client_id=client.client_id,
        odoo_user_id=presented.odoo_user_id,
        grant_id=presented.grant_id,
    )

    return IssuedTokens(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=int(ACCESS_TOKEN_TTL.total_seconds()),
        scope=presented.scope,
    )


async def revoke(
    session: AsyncSession,
    *,
    client_id: str,
    client_secret: str | None,
    token: str,
) -> None:
    """RFC 7009 revoke. Tries access-token hash first, then refresh-token.

    Per spec, the endpoint returns 200 even for unknown tokens (so clients
    can't probe whether a token exists). Raises TokenError only for client
    authentication failures.
    """
    client = await _authenticate_client(session, client_id, client_secret)
    now = datetime.now(UTC)
    token_hash = _hash(token)

    access = (
        await session.execute(
            select(AccessToken).where(AccessToken.token_hash == token_hash)
        )
    ).scalar_one_or_none()
    if access and access.client_id == client.client_id and access.revoked_at is None:
        # Revoke the entire grant family — invalidate every access token
        # under this grant_id plus the refresh chain.
        await session.execute(
            update(AccessToken)
            .where(AccessToken.grant_id == access.grant_id)
            .values(revoked_at=now)
        )
        await session.execute(
            update(RefreshToken)
            .where(RefreshToken.grant_id == access.grant_id)
            .where(RefreshToken.consumed_at.is_(None))
            .values(consumed_at=now)
        )
        log.info("token_revoked", client_id=client.client_id, grant_id=access.grant_id)
        return

    refresh = (
        await session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
    ).scalar_one_or_none()
    if refresh and refresh.client_id == client.client_id:
        await session.execute(
            update(AccessToken)
            .where(AccessToken.grant_id == refresh.grant_id)
            .values(revoked_at=now)
        )
        await session.execute(
            update(RefreshToken)
            .where(RefreshToken.grant_id == refresh.grant_id)
            .where(RefreshToken.consumed_at.is_(None))
            .values(consumed_at=now)
        )
        log.info("token_revoked", client_id=client.client_id, grant_id=refresh.grant_id)


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
            odoo_api_key_value=auth_code.odoo_api_key_value,
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
