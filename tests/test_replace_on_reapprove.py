import base64
import hashlib
import json
import secrets
from collections.abc import Iterator

import httpx
import pytest
from httpx import AsyncClient

from app.services import upstream_keys

SECRET = {"X-Internal-Secret": "test-shared-secret"}
REDIRECT = "https://claude.ai/api/mcp/auth_callback"


@pytest.fixture
def revoked_key_ids() -> Iterator[list[int]]:
    ids: list[int] = []

    def handler(req: httpx.Request) -> httpx.Response:
        ids.append(json.loads(req.content)["api_key_id"])
        return httpx.Response(200, json={"revoked": True})

    transport = httpx.MockTransport(handler)
    upstream_keys.set_client_factory(lambda: httpx.AsyncClient(transport=transport))
    yield ids
    upstream_keys.reset_client_factory()


def _pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return verifier, base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


async def _approve(
    client: AsyncClient,
    *,
    app_name: str,
    odoo_user_id: int,
    api_key_id: int,
    browser_id: str | None,
) -> dict[str, str]:
    res = await client.post(
        "/register", json={"redirect_uris": [REDIRECT], "client_name": app_name}
    )
    client_id = res.json()["client_id"]
    verifier, challenge = _pkce()
    res = await client.get(
        "/authorize",
        params={
            "client_id": client_id,
            "redirect_uri": REDIRECT,
            "response_type": "code",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "scope": "omnidim:all",
            "state": "s",
        },
        follow_redirects=False,
    )
    request_id = res.headers["location"].rsplit("=", 1)[1]
    body: dict[str, object] = {
        "request_id": request_id,
        "odoo_user_id": odoo_user_id,
        "odoo_api_key_id": api_key_id,
        "odoo_api_key_value": f"key-{api_key_id}",
        "approved_scope": "omnidim:all",
    }
    if browser_id is not None:
        body["browser_id"] = browser_id
    res = await client.post("/internal/issue-code", headers=SECRET, json=body)
    assert res.status_code == 200, res.text
    res = await client.post(
        "/token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": res.json()["code"],
            "redirect_uri": REDIRECT,
            "code_verifier": verifier,
        },
    )
    assert res.status_code == 200, res.text
    return {"client_id": client_id, **res.json()}


async def _refresh(client: AsyncClient, grant: dict[str, str]) -> dict[str, str]:
    res = await client.post(
        "/token",
        data={
            "grant_type": "refresh_token",
            "client_id": grant["client_id"],
            "refresh_token": grant["refresh_token"],
        },
    )
    assert res.status_code == 200, res.text
    return {"client_id": grant["client_id"], **res.json()}


async def _mcp_status(client: AsyncClient, grant: dict[str, str]) -> int:
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {grant['access_token']}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
    )
    return res.status_code


def _browser() -> str:
    return secrets.token_urlsafe(32)


async def test_switching_account_in_same_browser_ends_old_grant(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    browser = _browser()
    demo = await _approve(
        client, app_name="Claude", odoo_user_id=33, api_key_id=101, browser_id=browser
    )
    mine = await _approve(
        client, app_name="Claude", odoo_user_id=150359, api_key_id=102, browser_id=browser
    )

    assert await _mcp_status(client, demo) == 401
    assert await _mcp_status(client, mine) == 200
    assert revoked_key_ids == [101]


async def test_reapproving_same_account_ends_old_grant(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    browser = _browser()
    first = await _approve(
        client, app_name="Claude", odoo_user_id=7, api_key_id=201, browser_id=browser
    )
    second = await _approve(
        client, app_name="Claude", odoo_user_id=7, api_key_id=202, browser_id=browser
    )

    assert await _mcp_status(client, first) == 401
    assert await _mcp_status(client, second) == 200
    assert revoked_key_ids == [201]


async def test_refreshed_grant_is_still_replaced(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    browser = _browser()
    demo = await _refresh(
        client,
        await _approve(
            client, app_name="Claude", odoo_user_id=33, api_key_id=301, browser_id=browser
        ),
    )
    await _approve(
        client, app_name="Claude", odoo_user_id=150359, api_key_id=302, browser_id=browser
    )

    assert await _mcp_status(client, demo) == 401
    assert revoked_key_ids == [301]


async def test_other_browser_keeps_its_grant(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    teammate = await _approve(
        client, app_name="Claude", odoo_user_id=33, api_key_id=401, browser_id=_browser()
    )
    await _approve(
        client, app_name="Claude", odoo_user_id=33, api_key_id=402, browser_id=_browser()
    )

    assert await _mcp_status(client, teammate) == 200
    assert revoked_key_ids == []


async def test_other_app_in_same_browser_keeps_its_grant(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    browser = _browser()
    chatgpt = await _approve(
        client, app_name="ChatGPT", odoo_user_id=9, api_key_id=501, browser_id=browser
    )
    await _approve(client, app_name="Claude", odoo_user_id=9, api_key_id=502, browser_id=browser)

    assert await _mcp_status(client, chatgpt) == 200
    assert revoked_key_ids == []


async def test_approval_without_browser_id_replaces_nothing(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    browser = _browser()
    old = await _approve(
        client, app_name="Claude", odoo_user_id=11, api_key_id=601, browser_id=browser
    )
    await _approve(client, app_name="Claude", odoo_user_id=12, api_key_id=602, browser_id=None)

    assert await _mcp_status(client, old) == 200
    assert revoked_key_ids == []


async def test_odoo_outage_still_connects_and_ends_old_grant(
    client: AsyncClient,
) -> None:
    def down(_req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("odoo down")

    transport = httpx.MockTransport(down)
    upstream_keys.set_client_factory(lambda: httpx.AsyncClient(transport=transport))
    try:
        browser = _browser()
        demo = await _approve(
            client, app_name="Claude", odoo_user_id=33, api_key_id=701, browser_id=browser
        )
        mine = await _approve(
            client, app_name="Claude", odoo_user_id=13, api_key_id=702, browser_id=browser
        )
    finally:
        upstream_keys.reset_client_factory()

    assert await _mcp_status(client, demo) == 401
    assert await _mcp_status(client, mine) == 200
