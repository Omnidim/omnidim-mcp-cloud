import asyncio
import secrets
from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import RefreshToken
from app.services.token import lock_grant, revoke_grants_locally
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
        json={"odoo_user_id": odoo_user_id, "apps": [app]},
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
        "/internal/connections/disconnect", json={"odoo_user_id": 1, "apps": ["Claude"]}
    )

    assert (listed.status_code, ended.status_code) == (401, 401)


async def test_disconnect_rejects_a_malformed_body(client: AsyncClient) -> None:
    res = await client.post(
        "/internal/connections/disconnect", headers=SECRET, json={"odoo_user_id": "x"}
    )

    assert res.status_code == 422


async def test_disconnect_also_ends_a_refresh_that_was_in_flight(
    client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
    revoked_key_ids: list[int],
) -> None:
    user = new_user_id()
    await approve(client, app_name="Claude", odoo_user_id=user, api_key_id=851, browser_id=None)
    async with session_factory() as refreshing:
        grant_id = (
            await refreshing.execute(
                text("SELECT grant_id FROM oauth_refresh_token WHERE odoo_user_id = :u"),
                {"u": user},
            )
        ).scalar_one()
        await lock_grant(refreshing, grant_id)
        disconnecting = asyncio.create_task(_disconnect(client, user, "Claude"))
        await asyncio.sleep(0.3)
        now = datetime.now(UTC)
        await refreshing.execute(
            text(
                "UPDATE oauth_refresh_token SET consumed_at = :now "
                "WHERE grant_id = :g AND consumed_at IS NULL"
            ),
            {"now": now, "g": grant_id},
        )
        refreshing.add(
            RefreshToken(
                token_hash=secrets.token_hex(32),
                client_id=(
                    await refreshing.execute(
                        text("SELECT client_id FROM oauth_refresh_token WHERE grant_id = :g"),
                        {"g": grant_id},
                    )
                )
                .scalars()
                .first(),
                odoo_user_id=user,
                grant_id=grant_id,
                scope="omnidim:all",
                expires_at=now + timedelta(days=90),
            )
        )
        await refreshing.commit()

    assert await disconnecting == 1
    assert await _connections(client, user) == []


async def test_one_disconnect_ends_every_name_of_a_row(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    user = new_user_id()
    for key, name in ((861, "Claude Code (omnidim)"), (862, "Claude Code (omnidimension)")):
        await approve(client, app_name=name, odoo_user_id=user, api_key_id=key, browser_id=None)

    res = await client.post(
        "/internal/connections/disconnect",
        headers=SECRET,
        json={
            "odoo_user_id": user,
            "apps": ["Claude Code (omnidim)", "Claude Code (omnidimension)"],
        },
    )

    assert res.json() == {"disconnected": 2}
    assert await _connections(client, user) == []


async def test_disconnect_rejects_an_empty_app_list(client: AsyncClient) -> None:
    res = await client.post(
        "/internal/connections/disconnect", headers=SECRET, json={"odoo_user_id": 1, "apps": []}
    )

    assert res.status_code == 422


async def test_refresh_waiting_on_a_disconnect_is_refused(
    client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
    revoked_key_ids: list[int],
) -> None:
    user = new_user_id()
    grant = await approve(
        client, app_name="Claude", odoo_user_id=user, api_key_id=871, browser_id=None
    )
    async with session_factory() as disconnecting:
        grant_id = (
            await disconnecting.execute(
                text("SELECT grant_id FROM oauth_refresh_token WHERE odoo_user_id = :u"),
                {"u": user},
            )
        ).scalar_one()
        await revoke_grants_locally(disconnecting, [grant_id], datetime.now(UTC))
        refreshing = asyncio.create_task(
            client.post(
                "/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": grant["client_id"],
                    "refresh_token": grant["refresh_token"],
                },
            )
        )
        await asyncio.sleep(0.3)
        await disconnecting.commit()

    assert (await refreshing).status_code == 400
    assert await _connections(client, user) == []


async def test_names_the_website_each_app_signed_in_through(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    user = new_user_id()
    glama = ["https://glama.ai/api/app/mcp/oauth/callback", "http://localhost:6749/callback"]
    vscode = ["http://127.0.0.1:33418/", "https://insiders.vscode.dev/redirect"]
    spoof = ["https://evil.example/cb", "https://claude.ai/api/mcp/auth_callback"]
    apps = (
        (871, "Glama", glama),
        (872, "Cursor", ["https://www.cursor.com/agents/mcp/oauth/callback"]),
        (873, "Visual Studio Code", vscode),
        (874, "Codex", ["http://127.0.0.1:50044/callback"]),
        (875, "Clauude", spoof),
    )
    for key, name, uris in apps:
        await approve(
            client,
            app_name=name,
            odoo_user_id=user,
            api_key_id=key,
            browser_id=None,
            redirect_uris=uris,
        )

    rows = await _connections(client, user)

    assert {r["app"]: r["site"] for r in rows} == {
        "Glama": "glama.ai",
        "Cursor": "cursor.com",
        "Visual Studio Code": None,
        "Codex": None,
        "Clauude": "evil.example",
    }


async def test_prefers_a_website_when_one_app_signed_in_both_ways(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    user = new_user_id()
    for key, uri in ((881, "http://localhost:8787/callback"), (882, "https://cursor.com/cb")):
        await approve(
            client,
            app_name="Cursor",
            odoo_user_id=user,
            api_key_id=key,
            browser_id=None,
            redirect_uris=[uri],
        )

    assert [r["site"] for r in await _connections(client, user)] == ["cursor.com"]
