"""POST /internal/issue-token: Odoo mints an access token for an operator session."""
import json
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import pytest
from httpx import AsyncClient
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app._generated.tools import TOOLS
from app.config import get_settings
from app.models import AccessToken, OAuthClient, RefreshToken
from app.procedures import EXTRA_TOOLS
from app.services import dispatcher, upstream_keys
from tests.test_mcp_transport import _mint_access_token

ALL_TOOLS = {t["name"] for t in (*TOOLS, *EXTRA_TOOLS)}
OPERATOR_ONLY = {t["name"] for t in TOOLS if t.get("operator_only")}

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
    assert {t["name"] for t in res.json()["result"]["tools"]} == ALL_TOOLS


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



@pytest.fixture
def tool_upstream() -> Iterator[list[httpx.Request]]:
    captured: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        captured.append(req)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    dispatcher.set_client_factory(lambda: httpx.AsyncClient(transport=transport))
    yield captured
    dispatcher.reset_client_factory()


async def _issue_read(client: AsyncClient) -> dict[str, object]:
    res = await client.post(
        "/internal/issue-token", headers=SECRET, json={**BODY, "scope": "omnidim:read"}
    )
    assert res.status_code == 200, res.text
    data: dict[str, object] = res.json()
    return data


async def _call(client: AsyncClient, token: object, name: str) -> httpx.Response:
    return await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": {}},
        },
    )


READ_TOOLS = {t["name"] for t in (*TOOLS, *EXTRA_TOOLS) if t["annotations"].get("readOnlyHint")}


def test_read_only_marking() -> None:
    assert "dispatchCall" not in READ_TOOLS
    assert {"listAgents", "getCallLog", "getCallEvents", "readGuide"} <= READ_TOOLS
    # A merged tool (one per several operations) is read-only only when every action is a GET.
    def methods(t: dict[str, Any]) -> set[str]:
        return {a["method"] for a in t["actions"].values()} if "actions" in t else {t["method"]}

    assert all(methods(t) != {"GET"} or t["name"] in READ_TOOLS for t in TOOLS)


async def test_read_scope_is_stored(
    client: AsyncClient, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    data = await _issue_read(client)
    assert data["scope"] == "omnidim:read"
    async with session_factory() as session:
        row = (
            await session.execute(
                select(AccessToken).where(AccessToken.grant_id == data["grant_id"])
            )
        ).scalar_one()
    assert row.scope == "omnidim:read"


@pytest.mark.parametrize("scope", ["omnidim:write", "", "omnidim:read omnidim:all", "admin"])
async def test_unknown_scope_is_400(client: AsyncClient, scope: str) -> None:
    res = await client.post(
        "/internal/issue-token", headers=SECRET, json={**BODY, "scope": scope}
    )
    assert res.status_code == 400
    assert res.json()["detail"]["error"] == "invalid_scope"


async def test_read_token_lists_only_read_tools(client: AsyncClient) -> None:
    token = (await _issue_read(client))["access_token"]
    tools = (await _mcp(client, token, "tools/list")).json()["result"]["tools"]
    assert {t["name"] for t in tools} == READ_TOOLS
    assert all(t["annotations"]["readOnlyHint"] for t in tools)


@pytest.mark.parametrize("name", sorted(ALL_TOOLS - READ_TOOLS))
async def test_read_token_write_tool_is_refused_without_upstream_call(
    client: AsyncClient, tool_upstream: list[httpx.Request], name: str
) -> None:
    token = (await _issue_read(client))["access_token"]
    res = await _call(client, token, name)
    assert res.status_code == 200
    error = res.json()["error"]
    assert error["message"] == "insufficient_scope"
    assert error["data"] == {"tool": name, "required_scope": "omnidim:all"}
    assert tool_upstream == []


async def test_read_token_can_call_read_tool(
    client: AsyncClient, tool_upstream: list[httpx.Request]
) -> None:
    token = (await _issue_read(client))["access_token"]
    res = await _call(client, token, "listAgents")
    assert "error" not in res.json()
    assert [r.method for r in tool_upstream] == ["GET"]


async def test_all_scope_token_can_call_write_tool(
    client: AsyncClient, tool_upstream: list[httpx.Request]
) -> None:
    token = (await _issue(client))["access_token"]
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "dispatchCall", "arguments": {"agent_id": 1, "to_number": "+1"}},
        },
    )
    assert "error" not in res.json()
    assert [r.method for r in tool_upstream] == ["POST"]


SUPPORT_TOOLS = {
    "getCallEvents": True,
    "getPlanAndAddons": True,
    "getSupportCase": True,
    "createSupportCase": False,
    "addCaseMessage": False,
}


def test_support_tools_exist_with_read_only_flags() -> None:
    by_name = {t["name"]: t for t in TOOLS}
    assert {n: by_name[n]["annotations"]["readOnlyHint"] for n in SUPPORT_TOOLS} == SUPPORT_TOOLS
    # The reads are public now (omnidim-docs #255, #256); only the writes stay operator-only.
    assert {n for n, read in SUPPORT_TOOLS.items() if not read} == OPERATOR_ONLY
    assert by_name["getCallEvents"]["path_params"] == ["call_log_id"]
    assert "user_id" not in by_name["getCallEvents"]["input_schema"]["properties"]


async def test_read_token_gets_call_events_but_cannot_create_case(
    client: AsyncClient, tool_upstream: list[httpx.Request]
) -> None:
    token = (await _issue_read(client))["access_token"]
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "getCallEvents", "arguments": {"call_log_id": 42}},
        },
    )
    assert "error" not in res.json()
    assert [(r.method, r.url.path) for r in tool_upstream] == [
        ("GET", "/api/v1/calls/logs/42/events")
    ]

    res = await _call(client, token, "createSupportCase")
    assert res.json()["error"]["message"] == "insufficient_scope"
    assert len(tool_upstream) == 1


async def test_oauth_client_never_sees_operator_tools(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    for path in ("/mcp", "/mcp/readonly"):
        res = await client.post(
            path,
            headers={"Authorization": f"Bearer {token}"},
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        )
        names = {t["name"] for t in res.json()["result"]["tools"]}
        assert names and not names & OPERATOR_ONLY


@pytest.mark.parametrize("name", sorted(OPERATOR_ONLY))
async def test_oauth_client_cannot_call_operator_tools(
    client: AsyncClient, tool_upstream: list[httpx.Request], name: str
) -> None:
    token = await _mint_access_token(client)
    res = await _call(client, token, name)
    assert res.json()["error"]["message"] == f"unknown tool: {name}"
    assert tool_upstream == []


async def test_ping_works_for_operator_token(client: AsyncClient) -> None:
    token = (await _issue_read(client))["access_token"]
    assert (await _mcp(client, token, "ping")).json()["result"] == {}
