import httpx
from httpx import AsyncClient

from app.services import upstream_keys
from tests.oauth_flow import approve, mcp_status, new_browser_id, refresh


async def test_switching_account_in_same_browser_ends_old_grant(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    browser = new_browser_id()
    demo = await approve(
        client, app_name="Claude", odoo_user_id=33, api_key_id=101, browser_id=browser
    )
    mine = await approve(
        client, app_name="Claude", odoo_user_id=150359, api_key_id=102, browser_id=browser
    )

    assert await mcp_status(client, demo) == 401
    assert await mcp_status(client, mine) == 200
    assert revoked_key_ids == [101]


async def test_reapproving_same_account_ends_old_grant(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    browser = new_browser_id()
    first = await approve(
        client, app_name="Claude", odoo_user_id=7, api_key_id=201, browser_id=browser
    )
    second = await approve(
        client, app_name="Claude", odoo_user_id=7, api_key_id=202, browser_id=browser
    )

    assert await mcp_status(client, first) == 401
    assert await mcp_status(client, second) == 200
    assert revoked_key_ids == [201]


async def test_refreshed_grant_is_still_replaced(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    browser = new_browser_id()
    demo = await refresh(
        client,
        await approve(
            client, app_name="Claude", odoo_user_id=33, api_key_id=301, browser_id=browser
        ),
    )
    await approve(
        client, app_name="Claude", odoo_user_id=150359, api_key_id=302, browser_id=browser
    )

    assert await mcp_status(client, demo) == 401
    assert revoked_key_ids == [301]


async def test_other_browser_keeps_its_grant(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    teammate = await approve(
        client, app_name="Claude", odoo_user_id=33, api_key_id=401, browser_id=new_browser_id()
    )
    await approve(
        client, app_name="Claude", odoo_user_id=33, api_key_id=402, browser_id=new_browser_id()
    )

    assert await mcp_status(client, teammate) == 200
    assert revoked_key_ids == []


async def test_other_app_in_same_browser_keeps_its_grant(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    browser = new_browser_id()
    chatgpt = await approve(
        client, app_name="ChatGPT", odoo_user_id=9, api_key_id=501, browser_id=browser
    )
    await approve(client, app_name="Claude", odoo_user_id=9, api_key_id=502, browser_id=browser)

    assert await mcp_status(client, chatgpt) == 200
    assert revoked_key_ids == []


async def test_approval_without_browser_id_replaces_nothing(
    client: AsyncClient, revoked_key_ids: list[int]
) -> None:
    browser = new_browser_id()
    old = await approve(
        client, app_name="Claude", odoo_user_id=11, api_key_id=601, browser_id=browser
    )
    await approve(client, app_name="Claude", odoo_user_id=12, api_key_id=602, browser_id=None)

    assert await mcp_status(client, old) == 200
    assert revoked_key_ids == []


async def test_odoo_outage_still_connects_and_ends_old_grant(
    client: AsyncClient,
) -> None:
    def down(_req: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("odoo down")

    transport = httpx.MockTransport(down)
    upstream_keys.set_client_factory(lambda: httpx.AsyncClient(transport=transport))
    try:
        browser = new_browser_id()
        demo = await approve(
            client, app_name="Claude", odoo_user_id=33, api_key_id=701, browser_id=browser
        )
        mine = await approve(
            client, app_name="Claude", odoo_user_id=13, api_key_id=702, browser_id=browser
        )
    finally:
        upstream_keys.reset_client_factory()

    assert await mcp_status(client, demo) == 401
    assert await mcp_status(client, mine) == 200
