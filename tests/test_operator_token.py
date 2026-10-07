"""POST /internal/issue-token: Odoo mints an access token for an operator session."""
import json
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from httpx import AsyncClient
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app._generated.tools import TOOLS
from app.config import get_settings
from app.models import AccessToken, OAuthClient, RefreshToken
from app.services import upstream_keys

SECRET = {"X-Internal-Secret": "test-shared-secret"}
API_KEY_ID = 777
BODY = {"odoo_user_id": 2943, "odoo_api_key_id": API_KEY_ID, "odoo_api_key_value": "k-plain"}


@pytest.fixture
def upstream_requests() -> Iterator[list[httpx.Request]]:
    captured: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        captured.append(req)
        return httpx.Response(200, json={"revoked": True})

    transport = httpx.MockTransport(handler)
    upstream_keys.set_client_factory(lambda: httpx.AsyncClient(transport=transport))
    yield captured
    upstream_keys.reset_client_factory()


async def _issue(client: AsyncClient) -> dict[str, object]:
    res = await client.post("/internal/issue-token", headers=SECRET, json=BODY)
    assert res.status_code == 200, res.text
    data: dict[str, object] = res.json()
    return data


async def _mcp(client: AsyncClient, token: object, method: str) -> httpx.Response:
    return await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": method},
    )


async def test_rejected_without_secret(client: AsyncClient) -> None:
    assert (await client.post("/internal/issue-token", json=BODY)).status_code == 401
    res = await client.post(
        "/internal/issue-token", headers={"X-Internal-Secret": "nope"}, json=BODY
    )
    assert res.status_code == 401


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"odoo_user_id": 1, "odoo_api_key_id": 2},
        {"odoo_user_id": "x", "odoo_api_key_id": 2, "odoo_api_key_value": "k"},
        {"odoo_user_id": 1, "odoo_api_key_id": 2, "odoo_api_key_value": ""},
        {"odoo_user_id": 0, "odoo_api_key_id": 2, "odoo_api_key_value": "k"},
        {"odoo_user_id": 1, "odoo_api_key_id": -1, "odoo_api_key_value": "k"},
    ],
)
async def test_bad_body_is_422(client: AsyncClient, body: dict[str, object]) -> None:
    res = await client.post("/internal/issue-token", headers=SECRET, json=body)
    assert res.status_code == 422


async def test_issued_token_shape_and_ttl(
    client: AsyncClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    data = await _issue(client)
    assert data["token_type"] == "Bearer"  # noqa: S105
    assert data["scope"] == "omnidim:all"
    assert data["expires_in"] == get_settings().access_token_ttl_seconds
    assert isinstance(data["grant_id"], str)
    assert "refresh_token" not in data

    async with session_factory() as session:
        row = (
            await session.execute(
                select(AccessToken).where(AccessToken.grant_id == data["grant_id"])
            )
        ).scalar_one()
        refresh_rows = (
            await session.execute(
                select(func.count())
                .select_from(RefreshToken)
                .where(RefreshToken.grant_id == data["grant_id"])
            )
        ).scalar_one()
    assert row.client_id == get_settings().operator_client_id
    assert row.odoo_user_id == 2943
    assert row.odoo_api_key_id == API_KEY_ID
    assert row.odoo_api_key_value not in (None, "k-plain")
    assert row.token_hash != data["access_token"]
    assert refresh_rows == 0


async def test_ttl_follows_setting(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "access_token_ttl_seconds", 120)
    assert (await _issue(client))["expires_in"] == 120


async def test_token_works_on_mcp_and_lists_all_tools(client: AsyncClient) -> None:
    token = (await _issue(client))["access_token"]
    res = await _mcp(client, token, "tools/list")
    assert res.status_code == 200
    assert {t["name"] for t in res.json()["result"]["tools"]} == {t["name"] for t in TOOLS}


async def test_expired_token_rejected(
    client: AsyncClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    data = await _issue(client)
    async with session_factory() as session:
        await session.execute(
            update(AccessToken)
            .where(AccessToken.grant_id == data["grant_id"])
            .values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
        )
        await session.commit()
    assert (await _mcp(client, data["access_token"], "tools/list")).status_code == 401


async def test_revoking_grant_revokes_upstream_key(
    client: AsyncClient, upstream_requests: list[httpx.Request]
) -> None:
    data = await _issue(client)
    res = await client.post(
        "/revoke",
        data={"client_id": get_settings().operator_client_id, "token": data["access_token"]},
    )
    assert res.status_code == 200
    assert len(upstream_requests) == 1
    assert json.loads(upstream_requests[0].content) == {"api_key_id": API_KEY_ID}
    assert (await _mcp(client, data["access_token"], "tools/list")).status_code == 401


async def test_repeat_issue_is_idempotent_for_client_row(
    client: AsyncClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    first = await _issue(client)
    second = await _issue(client)
    assert first["grant_id"] != second["grant_id"]
    async with session_factory() as session:
        count = (
            await session.execute(
                select(func.count())
                .select_from(OAuthClient)
                .where(OAuthClient.client_id == get_settings().operator_client_id)
            )
        ).scalar_one()
    assert count == 1


@pytest.mark.parametrize(
    "form",
    [
        {
            "grant_type": "authorization_code",
            "code": "any",
            "redirect_uri": "http://localhost/cb",
            "code_verifier": "v" * 43,
        },
        {"grant_type": "refresh_token", "refresh_token": "any"},
    ],
)
async def test_operator_client_rejected_at_token_endpoint(
    client: AsyncClient, form: dict[str, str]
) -> None:
    await _issue(client)
    res = await client.post(
        "/token", data={**form, "client_id": get_settings().operator_client_id}
    )
    assert res.status_code == 401
    assert res.json()["detail"]["error"] == "invalid_client"

