import base64
from collections.abc import Callable
from typing import Any

import httpx
import pytest
from httpx import AsyncClient, Response

from app.routes.mcp import SERVER_INFO
from tests.test_mcp_transport import _mint_access_token, mock_backend  # noqa: F401

MODERN = "2026-07-28"
LEGACY = "2025-11-25"
NAMED = {"tools/call": "name", "prompts/get": "name", "resources/read": "uri"}


def _meta(version: str) -> dict[str, Any]:
    return {
        "io.modelcontextprotocol/protocolVersion": version,
        "io.modelcontextprotocol/clientInfo": {"name": "Claude Code", "version": "2.1.331"},
        "io.modelcontextprotocol/clientCapabilities": {},
    }


async def _modern(
    client: AsyncClient,
    token: str,
    method: str,
    params: dict[str, Any] | None = None,
    *,
    path: str = "/mcp",
    version: str = MODERN,
    headers: dict[str, str | None] | None = None,
) -> Response:
    sent: dict[str, str | None] = {
        "Authorization": f"Bearer {token}",
        "MCP-Protocol-Version": version,
        "Mcp-Method": method,
    }
    if method in NAMED:
        sent["Mcp-Name"] = str((params or {})[NAMED[method]])
    sent.update(headers or {})
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {**(params or {}), "_meta": _meta(version)},
    }
    return await client.post(
        path, json=body, headers={k: v for k, v in sent.items() if v is not None}
    )


async def test_discover_advertises_both_eras_and_the_skills_extension(
    client: AsyncClient,
) -> None:
    token = await _mint_access_token(client)

    res = await _modern(client, token, "server/discover")

    result = res.json()["result"]
    assert res.status_code == 200
    assert result["supportedVersions"] == [MODERN, LEGACY]
    assert result["capabilities"]["extensions"] == {"io.modelcontextprotocol/skills": {}}
    assert {"tools", "prompts", "resources"} <= set(result["capabilities"])
    assert "readGuide" in result["instructions"]
    assert result["resultType"] == "complete"
    assert result["_meta"]["io.modelcontextprotocol/serverInfo"] == SERVER_INFO
    assert result["ttlMs"] > 0
    assert result["cacheScope"] == "public"


@pytest.mark.parametrize(
    ("method", "params"),
    [
        ("tools/list", None),
        ("prompts/list", None),
        ("resources/list", None),
        ("resources/templates/list", None),
        ("resources/read", {"uri": "omnidim://guide/routing"}),
        ("skills/list", None),
        ("skills/get", {"uri": "skill://omnidim-audit-calls/SKILL.md"}),
    ],
)
async def test_cacheable_results_carry_a_result_type_and_cache_hints(
    client: AsyncClient, method: str, params: dict[str, Any] | None
) -> None:
    token = await _mint_access_token(client)

    result = (await _modern(client, token, method, params)).json()["result"]

    assert result["resultType"] == "complete"
    assert result["ttlMs"] > 0
    assert result["cacheScope"] == "public"


async def test_modern_tools_list_serves_the_same_tools_as_legacy(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    legacy = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
    )

    modern = (await _modern(client, token, "tools/list")).json()["result"]

    assert modern["tools"] == legacy.json()["result"]["tools"]


async def test_modern_tool_call_runs_and_is_not_cacheable(
    client: AsyncClient,
    mock_backend: Callable[[Callable[[httpx.Request], httpx.Response]], list[httpx.Request]],  # noqa: F811
) -> None:
    token = await _mint_access_token(client)
    captured = mock_backend(lambda req: httpx.Response(200, json={"bots": []}))

    res = await _modern(client, token, "tools/call", {"name": "listAgents", "arguments": {}})

    result = res.json()["result"]
    assert len(captured) == 1
    assert result["resultType"] == "complete"
    assert result["isError"] is False
    assert "ttlMs" not in result


async def test_unsupported_version_lists_what_the_server_speaks(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    res = await _modern(client, token, "tools/list", version="1900-01-01")

    assert res.status_code == 400
    error = res.json()["error"]
    assert error["code"] == -32022
    assert error["data"] == {"supported": [MODERN, LEGACY], "requested": "1900-01-01"}


@pytest.mark.parametrize(
    ("method", "params", "headers"),
    [
        ("tools/list", None, {"MCP-Protocol-Version": None}),
        ("tools/list", None, {"MCP-Protocol-Version": LEGACY}),
        ("tools/list", None, {"Mcp-Method": None}),
        ("tools/list", None, {"Mcp-Method": "prompts/list"}),
        ("resources/read", {"uri": "omnidim://guide/routing"}, {"Mcp-Name": None}),
        ("resources/read", {"uri": "omnidim://guide/routing"}, {"Mcp-Name": "omnidim://x"}),
        ("resources/read", {"uri": "omnidim://guide/routing"}, {"Mcp-Name": "=?base64?%%?="}),
    ],
)
async def test_headers_that_disagree_with_the_body_are_refused(
    client: AsyncClient,
    method: str,
    params: dict[str, Any] | None,
    headers: dict[str, str | None],
) -> None:
    token = await _mint_access_token(client)

    res = await _modern(client, token, method, params, headers=headers)

    assert res.status_code == 400
    assert res.json()["error"]["code"] == -32020


async def test_a_tool_call_with_the_wrong_name_header_never_reaches_the_api(
    client: AsyncClient,
    mock_backend: Callable[[Callable[[httpx.Request], httpx.Response]], list[httpx.Request]],  # noqa: F811
) -> None:
    token = await _mint_access_token(client)
    captured = mock_backend(lambda req: httpx.Response(200, json={"ok": True}))

    res = await _modern(
        client, token, "tools/call",
        {"name": "deleteAgent", "arguments": {"agent_id": 1}},
        headers={"Mcp-Name": "listAgents"},
    )

    assert res.status_code == 400
    assert captured == []


async def test_a_base64_name_header_is_decoded_before_the_check(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    uri = "omnidim://guide/routing"
    encoded = "=?base64?" + base64.b64encode(uri.encode()).decode() + "?="

    res = await _modern(
        client, token, "resources/read", {"uri": uri}, headers={"Mcp-Name": encoded}
    )

    assert res.status_code == 200
    assert res.json()["result"]["contents"][0]["uri"] == uri


@pytest.mark.parametrize("method", ["tasks/get", "initialize", "ping"])
async def test_methods_outside_2026_07_28_are_not_found(client: AsyncClient, method: str) -> None:
    token = await _mint_access_token(client)

    res = await _modern(client, token, method)

    assert res.status_code == 404
    assert res.json()["error"]["code"] == -32601


async def test_modern_errors_keep_their_json_rpc_code(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    res = await _modern(client, token, "skills/get", {"uri": "skill://nope/SKILL.md"})

    assert res.status_code == 200
    assert res.json()["error"]["code"] == -32602


async def test_discover_needs_a_token(client: AsyncClient) -> None:
    res = await client.post(
        "/mcp",
        headers={"MCP-Protocol-Version": MODERN, "Mcp-Method": "server/discover"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "server/discover",
            "params": {"_meta": _meta(MODERN)},
        },
    )

    assert res.status_code == 401


async def test_legacy_handshake_is_unchanged(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}", "MCP-Protocol-Version": LEGACY},
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
    )

    result = res.json()["result"]
    assert result["protocolVersion"] == LEGACY
    assert "extensions" not in result["capabilities"]
    assert "resultType" not in result


@pytest.mark.parametrize(
    ("method", "params", "code"),
    [
        ("server/discover", None, -32601),
        ("skills/list", None, -32601),
        ("skills/get", {"uri": "skill://omnidim-audit-calls/SKILL.md"}, -32601),
        ("resources/read", {"uri": "skill://omnidim-audit-calls/SKILL.md"}, -32602),
    ],
)
async def test_legacy_requests_get_no_modern_methods(
    client: AsyncClient, method: str, params: dict[str, Any] | None, code: int
) -> None:
    token = await _mint_access_token(client)
    body: dict[str, Any] = {"jsonrpc": "2.0", "id": 1, "method": method}
    if params is not None:
        body["params"] = params

    res = await client.post("/mcp", headers={"Authorization": f"Bearer {token}"}, json=body)

    assert res.json()["error"]["code"] == code


@pytest.mark.parametrize("params", ["x", 5, ["a"]])
async def test_params_that_are_not_an_object_are_invalid(client: AsyncClient, params: Any) -> None:
    token = await _mint_access_token(client)

    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "ping", "params": params},
    )

    assert res.json()["error"]["code"] == -32602


async def test_a_notification_gets_no_answer_whatever_its_params(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "method": "notifications/initialized", "params": "x"},
    )

    assert res.status_code == 202
    assert res.content == b""


async def test_legacy_results_carry_no_modern_fields(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}", "MCP-Protocol-Version": LEGACY},
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
    )

    assert set(res.json()["result"]) == {"tools"}
