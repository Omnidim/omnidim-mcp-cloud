"""MCP tool annotations: unit logic + tools/list wiring."""
from httpx import AsyncClient

from app.annotations import tool_annotations

from .test_mcp_transport import _mint_access_token


def test_get_tools_are_read_only() -> None:
    a = tool_annotations("listAgents", "GET")
    assert a["readOnlyHint"] is True
    assert a["openWorldHint"] is False
    assert "destructiveHint" not in a
    assert a["title"] == "List agents"


def test_preview_posts_are_read_only() -> None:
    assert tool_annotations("canUploadFile", "POST")["readOnlyHint"] is True
    assert tool_annotations("calculateCreditOperation", "POST")["readOnlyHint"] is True


def test_plain_writes_are_not_destructive() -> None:
    a = tool_annotations("createAgent", "POST")
    assert a["readOnlyHint"] is False
    assert a["destructiveHint"] is False
    assert a["openWorldHint"] is False


def test_removals_are_destructive_not_open_world() -> None:
    for name in ("deleteAgent", "cancelBulkCall", "detachPhoneNumber", "revertCreditsFromChild"):
        a = tool_annotations(name, "POST")
        assert a["destructiveHint"] is True, name
        assert a["openWorldHint"] is False, name


def test_call_placing_tools_are_destructive_and_open_world() -> None:
    for name in ("dispatchCall", "createBulkCall", "addBulkCallContact"):
        a = tool_annotations(name, "POST")
        assert a["destructiveHint"] is True, name
        assert a["openWorldHint"] is True, name


async def test_tools_list_includes_annotations(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
    )
    tools = res.json()["result"]["tools"]
    assert tools
    by_name = {t["name"]: t for t in tools}
    assert all("annotations" in t for t in tools)
    assert by_name["dispatchCall"]["annotations"]["destructiveHint"] is True
    assert by_name["dispatchCall"]["annotations"]["openWorldHint"] is True
    assert by_name["listAgents"]["annotations"]["readOnlyHint"] is True
