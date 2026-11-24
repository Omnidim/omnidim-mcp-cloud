from __future__ import annotations

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.oauth import AppConnection
from app.services.token import revoke_grants_locally


async def list_connections(
    session: AsyncSession, odoo_user_id: int, now: datetime
) -> list[AppConnection]:
    rows = await session.execute(
        text(
            """
            SELECT c.client_name AS app,
                   count(DISTINCT r.grant_id) AS connections,
                   min(a.created_at) AS connected_at,
                   max(a.created_at) AS last_active_at
            FROM oauth_refresh_token r
            JOIN oauth_client c ON c.client_id = r.client_id
            JOIN oauth_access_token a ON a.grant_id = r.grant_id
            WHERE r.odoo_user_id = :odoo_user_id
              AND r.consumed_at IS NULL
              AND r.expires_at > :now
            GROUP BY c.client_name
            ORDER BY max(a.created_at) DESC
            """
        ),
        {"odoo_user_id": odoo_user_id, "now": now},
    )
    return [AppConnection.model_validate(row) for row in rows.mappings()]


async def end_connections(
    session: AsyncSession, odoo_user_id: int, apps: list[str], now: datetime
) -> dict[str, list[int]]:
    rows = await session.execute(
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
    return await revoke_grants_locally(session, list(rows.scalars()), now)
