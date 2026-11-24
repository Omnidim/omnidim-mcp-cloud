from httpx import AsyncClient

from tests.oauth_flow import SECRET, approve, mcp_status, new_browser_id, new_user_id, refresh


async def _connections(client: AsyncClient, odoo_user_id: int) -> list[dict[str, object]]:
    res = await client.get(f"/internal/connections/{odoo_user_id}", headers=SECRET)
    assert res.status_code == 200, res.text
    connections: list[dict[str, object]] = res.json()["connections"]
    return connections


async def _disconnect(client: AsyncClient, odoo_user_id: int, app: str) -> int:
    res = await client.post(
        "/internal/connections/disconnect",
        headers=SECRET,
        json={"odoo_user_id": odoo_user_id, "app": app},
    )
    assert res.status_code == 200, res.text
    disconnected: int = res.json()["disconnected"]
    return disconnected


async def test_lists_one_row_per_app(client: AsyncClient, revoked_key_ids: list[int]) -> None:
    user = new_user_id()
    for key in (801, 802):
        await approve(
            client,
            app_name="Claude",
            odoo_user_id=user,
            api_key_id=key,
            browser_id=new_browser_id(),
        )
    await approve(client, app_name="Cursor", odoo_user_id=user, api_key_id=803, browser_id=None)

    rows = await _connections(client, user)

    assert [(r["app"], r["connections"]) for r in rows] == [("Cursor", 1), ("Claude", 2)]
    assert all(r["connected_at"] and r["last_active_at"] for r in rows)


async def test_lists_only_this_users_live_connections(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    switched_from, switched_to, other = new_user_id(), new_user_id(), new_user_id()
    browser = new_browser_id()
    await approve(
        client, app_name="Claude", odoo_user_id=switched_from, api_key_id=811, browser_id=browser
    )
    await approve(
        client, app_name="Claude", odoo_user_id=switched_to, api_key_id=812, browser_id=browser
    )
    await approve(client, app_name="ChatGPT", odoo_user_id=other, api_key_id=813, browser_id=None)

    assert await _connections(client, switched_from) == []
    assert [r["app"] for r in await _connections(client, switched_to)] == ["Claude"]


async def test_refresh_keeps_one_connection_and_moves_last_active(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    user = new_user_id()
    grant = await approve(
        client, app_name="Claude", odoo_user_id=user, api_key_id=821, browser_id=None
    )
    before = (await _connections(client, user))[0]
    await refresh(client, grant)
    after = (await _connections(client, user))[0]

    assert after["connections"] == 1
    assert str(after["last_active_at"]) > str(before["last_active_at"])


async def test_disconnect_ends_every_connection_of_that_app_only(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    user = new_user_id()
    first = await approve(
        client, app_name="Claude", odoo_user_id=user, api_key_id=831, browser_id=new_browser_id()
    )
    second = await approve(
        client, app_name="Claude", odoo_user_id=user, api_key_id=832, browser_id=new_browser_id()
    )
    cursor = await approve(
        client, app_name="Cursor", odoo_user_id=user, api_key_id=833, browser_id=None
    )

    assert await _disconnect(client, user, "Claude") == 2

    assert await mcp_status(client, first) == 401
    assert await mcp_status(client, second) == 401
    assert await mcp_status(client, cursor) == 200
    assert sorted(revoked_key_ids) == [831, 832]
    assert [r["app"] for r in await _connections(client, user)] == ["Cursor"]


async def test_disconnect_never_touches_another_user(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    owner = new_user_id()
    theirs = await approve(
        client, app_name="Claude", odoo_user_id=owner, api_key_id=841, browser_id=None
    )

    assert await _disconnect(client, new_user_id(), "Claude") == 0
    assert await mcp_status(client, theirs) == 200
    assert revoked_key_ids == []


async def test_endpoints_refuse_without_the_shared_secret(client: AsyncClient) -> None:
    listed = await client.get("/internal/connections/1")
    ended = await client.post(
        "/internal/connections/disconnect", json={"odoo_user_id": 1, "app": "Claude"}
    )

    assert (listed.status_code, ended.status_code) == (401, 401)


async def test_disconnect_rejects_a_malformed_body(client: AsyncClient) -> None:
    res = await client.post(
        "/internal/connections/disconnect", headers=SECRET, json={"odoo_user_id": "x"}
    )

    assert res.status_code == 422
