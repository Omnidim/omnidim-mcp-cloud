"""/mcp/readonly serves only tools marked readOnlyHint, and refuses to run any other."""

from collections.abc import Callable
from typing import Any

import httpx
from httpx import AsyncClient

from app._generated.tools import TOOLS
from app.procedures import EXTRA_TOOLS
from tests.test_mcp_transport import _mint_access_token, mock_backend  # noqa: F401

READ_ONLY = {t["name"] for t in (*TOOLS, *EXTRA_TOOLS) if t["annotations"].get("readOnlyHint")}


async def _rpc(client: AsyncClient, token: str, path: str, method: str, params: Any = None) -> Any:
    body: dict[str, Any] = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        body["params"] = params
    res = await client.post(path, headers={"Authorization": f"Bearer {token}"}, json=body)
    return res.json()


async def test_readonly_lists_only_read_only_tools(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    tools = (await _rpc(client, token, "/mcp/readonly", "tools/list"))["result"]["tools"]

    names = {t["name"] for t in tools}
    assert names == READ_ONLY
    assert "listAgents" in names
    assert "dispatchCall" not in names


async def test_readonly_refuses_a_write_tool_without_calling_the_api(
    client: AsyncClient,
    mock_backend: Callable[[Callable[[httpx.Request], httpx.Response]], list[httpx.Request]],  # noqa: F811
) -> None:
    token = await _mint_access_token(client)
    captured = mock_backend(lambda req: httpx.Response(200, json={"ok": True}))

    body = await _rpc(
        client, token, "/mcp/readonly", "tools/call",
        {"name": "deleteAgent", "arguments": {"agent_id": 1}},
    )

    assert body["error"]["code"] == -32602
    assert "read-only" in body["error"]["message"]
    assert captured == []


async def test_readonly_runs_a_read_tool(
    client: AsyncClient,
    mock_backend: Callable[[Callable[[httpx.Request], httpx.Response]], list[httpx.Request]],  # noqa: F811
) -> None:
    token = await _mint_access_token(client)
    captured = mock_backend(lambda req: httpx.Response(200, json={"bots": []}))

    body = await _rpc(
        client, token, "/mcp/readonly", "tools/call", {"name": "listAgents", "arguments": {}}
    )

    assert body["result"]["isError"] is False
    assert len(captured) == 1


async def test_readonly_requires_bearer(client: AsyncClient) -> None:
    body = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    res = await client.post("/mcp/readonly", json=body)
    assert res.status_code == 401
    assert res.headers["WWW-Authenticate"].lower().startswith("bearer")


async def test_readonly_rejects_a_malformed_call(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    body = await _rpc(client, token, "/mcp/readonly", "tools/call", {"arguments": {}})

    assert body["error"]["code"] == -32602


async def test_full_endpoint_still_lists_every_tool(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    tools = (await _rpc(client, token, "/mcp", "tools/list"))["result"]["tools"]

    assert len(tools) == len(TOOLS) + len(EXTRA_TOOLS)
