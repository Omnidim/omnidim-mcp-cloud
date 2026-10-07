from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import structlog
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import AccessToken, OAuthClient
from app.scopes import DEFAULT_SCOPE
from app.security import encrypt_secret
from app.services.token import _generate_grant_id, _generate_token, _hash, access_token_ttl

log = structlog.get_logger()


@dataclass(frozen=True)
class IssuedOperatorToken:
    access_token: str
    expires_in: int
    scope: str
    grant_id: str


async def _ensure_operator_client(session: AsyncSession, client_id: str) -> None:
    await session.execute(
        insert(OAuthClient)
        .values(
            client_id=client_id,
            client_name="OmniOP Operator",
            redirect_uris=[],
            grant_types=[],
            response_types=[],
            scope=DEFAULT_SCOPE,
            token_endpoint_auth_method="none",  # noqa: S106 (spec literal)
            metadata_json={},
        )
        .on_conflict_do_nothing(index_elements=[OAuthClient.client_id])
    )


async def issue_operator_token(
    session: AsyncSession,
    *,
    odoo_user_id: int,
    odoo_api_key_id: int,
    odoo_api_key_value: str,
) -> IssuedOperatorToken:
    """Mint an access token for a first-party operator session. No refresh token:
    the operator reopens through Odoo when this one expires."""
    client_id = get_settings().operator_client_id
    await _ensure_operator_client(session, client_id)

    access_plain = _generate_token()
    grant_id = _generate_grant_id()
    ttl = access_token_ttl()
    session.add(
        AccessToken(
            token_hash=_hash(access_plain),
            client_id=client_id,
            odoo_user_id=odoo_user_id,
            odoo_api_key_id=odoo_api_key_id,
            odoo_api_key_value=encrypt_secret(odoo_api_key_value),
            grant_id=grant_id,
            scope=DEFAULT_SCOPE,
            expires_at=datetime.now(UTC) + ttl,
        )
    )
    log.info("operator_token_issued", odoo_user_id=odoo_user_id, grant_id=grant_id)
    return IssuedOperatorToken(
        access_token=access_plain,
        expires_in=int(ttl.total_seconds()),
        scope=DEFAULT_SCOPE,
        grant_id=grant_id,
    )
