from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AccessToken, OAuthClient
from app.security import decrypt_secret


@dataclass(frozen=True)
class ResolvedToken:
    odoo_user_id: int
    odoo_api_key_id: int
    odoo_api_key_value: str | None
    client_id: str
    scope: str
    # The app's self-declared name (Claude, ChatGPT, Cursor, ...), for logs only.
    client_name: str | None = None


class BearerError(Exception):
    def __init__(self, www_authenticate: str, description: str) -> None:
        super().__init__(description)
        self.www_authenticate = www_authenticate
        self.description = description


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def parse_authorization_header(header_value: str | None) -> str:
    if not header_value:
        raise BearerError(
            'Bearer realm="mcp.omnidim.io"',
            "missing Authorization header",
        )
    scheme, _, token = header_value.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise BearerError(
            'Bearer realm="mcp.omnidim.io", error="invalid_token"',
            "Authorization header must be 'Bearer <token>'",
        )
    return token.strip()


async def resolve_bearer(session: AsyncSession, header_value: str | None) -> ResolvedToken:
    token = parse_authorization_header(header_value)
    found = (
        await session.execute(
            select(AccessToken, OAuthClient.client_name)
            .outerjoin(OAuthClient, OAuthClient.client_id == AccessToken.client_id)
            .where(AccessToken.token_hash == _hash(token))
        )
    ).one_or_none()

    if found is None:
        raise BearerError(
            'Bearer realm="mcp.omnidim.io", error="invalid_token"',
            "access token not recognised",
        )
    row, client_name = found
    now = datetime.now(UTC)
    if row.revoked_at is not None:
        raise BearerError(
            'Bearer realm="mcp.omnidim.io", error="invalid_token",'
            ' error_description="token revoked"',
            "access token has been revoked",
        )
    if row.expires_at <= now:
        raise BearerError(
            'Bearer realm="mcp.omnidim.io", error="invalid_token",'
            ' error_description="token expired"',
            "access token has expired",
        )
    plaintext = decrypt_secret(row.odoo_api_key_value) if row.odoo_api_key_value else None
    return ResolvedToken(
        odoo_user_id=row.odoo_user_id,
        odoo_api_key_id=row.odoo_api_key_id,
        odoo_api_key_value=plaintext,
        client_id=row.client_id,
        scope=row.scope,
        client_name=client_name,
    )
