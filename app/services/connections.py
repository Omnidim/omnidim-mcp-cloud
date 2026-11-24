from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlsplit

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.token import revoke_grants_locally


@dataclass(frozen=True)
class Connection:
    app: str
    connections: int
    connected_at: datetime
    last_active_at: datetime
    used_redirects: list[str]


def web_site(used_redirects: list[str]) -> str | None:
    hosts = sorted(
        host.removeprefix("www.")
        for uri in used_redirects
        if (parts := urlsplit(uri)).scheme == "https" and (host := parts.hostname)
    )
    return hosts[0] if hosts else None


async def list_connections(
    session: AsyncSession, odoo_user_id: int, now: datetime
) -> list[Connection]:
    rows = await session.execute(
        text(
            """
            SELECT c.client_name, count(DISTINCT r.grant_id),
                   min(a.created_at), max(a.created_at),
                   array_remove(array_agg(DISTINCT code.redirect_uri), NULL)
            FROM oauth_refresh_token r
            JOIN oauth_client c ON c.client_id = r.client_id
            JOIN oauth_access_token a ON a.grant_id = r.grant_id
            LEFT JOIN oauth_authorization_code code
              ON code.client_id = r.client_id
             AND code.odoo_user_id = r.odoo_user_id
             AND code.consumed_at IS NOT NULL
            WHERE r.odoo_user_id = :odoo_user_id
              AND r.consumed_at IS NULL
              AND r.expires_at > :now
            GROUP BY c.client_name
            ORDER BY max(a.created_at) DESC
            """
        ),
        {"odoo_user_id": odoo_user_id, "now": now},
    )
    return [Connection(*row) for row in rows.tuples()]


async def end_connections(
    session: AsyncSession, odoo_user_id: int, apps: list[str], now: datetime
) -> dict[str, list[int]]:
    grant_ids = list(
        (
            await session.execute(
                text(
                    """
                    SELECT DISTINCT r.grant_id
                    FROM oauth_refresh_token r
                    JOIN oauth_client c ON c.client_id = r.client_id
                    WHERE r.odoo_user_id = :odoo_user_id
                      AND r.consumed_at IS NULL
                      AND r.expires_at > :now
                      AND c.client_name = ANY(:apps)
                    """
                ),
                {"odoo_user_id": odoo_user_id, "now": now, "apps": apps},
            )
        ).scalars()
    )
    return await revoke_grants_locally(session, grant_ids, now) if grant_ids else {}
