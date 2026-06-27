"""MCP procedure layer: prompts/list, prompts/get, resources/list, resources/read."""
from httpx import AsyncClient

from .test_mcp_transport import _mint_access_token


async def test_initialize_advertises_prompts_and_resources(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
    )
    caps = res.json()["result"]["capabilities"]
    assert "prompts" in caps
    assert "resources" in caps


async def test_prompts_list(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 2, "method": "prompts/list"},
    )
    prompts = res.json()["result"]["prompts"]
    names = {p["name"] for p in prompts}
    assert {"provision_agent", "audit_calls"} <= names
    prov = next(p for p in prompts if p["name"] == "provision_agent")
    assert any(a["name"] == "purpose" and a["required"] for a in prov["arguments"])


async def test_prompts_get_provision(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "prompts/get",
            "params": {
                "name": "provision_agent",
                "arguments": {"purpose": "book dental appointments", "test_number": "+15551234567"},
            },
        },
    )
    text = res.json()["result"]["messages"][0]["content"]["text"]
    assert "book dental appointments" in text
    assert "createAgent" in text
    assert "+15551234567" in text
    assert "call_conversation" in text


async def test_prompts_get_unknown(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 4, "method": "prompts/get", "params": {"name": "nope"}},
    )
    assert res.json()["error"]["code"] == -32602


async def test_resources_list_and_read(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 5, "method": "resources/list"},
    )
    uris = {r["uri"] for r in res.json()["result"]["resources"]}
    assert "omnidim://guide/routing" in uris

    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 6,
            "method": "resources/read",
            "params": {"uri": "omnidim://guide/routing"},
        },
    )
    text = res.json()["result"]["contents"][0]["text"]
    # The cloud server uses flat args; the guide must say so (not requestBody wrapping).
    assert "flat top-level arguments" in text


async def test_resources_read_unknown(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 7, "method": "resources/read", "params": {"uri": "omnidim://nope"}},
    )
    assert res.json()["error"]["code"] == -32602
