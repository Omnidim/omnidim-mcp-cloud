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


async def _read_resource(client: AsyncClient, token: str, uri: str) -> str:
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 8, "method": "resources/read", "params": {"uri": uri}},
    )
    return str(res.json()["result"]["contents"][0]["text"])


async def test_reference_resources_listed(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 8, "method": "resources/list"},
    )
    uris = {r["uri"] for r in res.json()["result"]["resources"]}
    assert {
        "omnidim://reference/recommended-stack",
        "omnidim://reference/voices",
        "omnidim://reference/agent-config",
    } <= uris


async def test_recommended_stack_uses_createagent_enums(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    text = await _read_resource(client, token, "omnidim://reference/recommended-stack")
    for token_str in ("azure_stream", "soniox", "sarvam", "cartesia", "gpt-4.1-mini"):
        assert token_str in text


async def test_agent_config_example_is_flat(client: AsyncClient) -> None:
    # The cloud server takes flat args, so the example must NOT wrap in a
    # requestBody object (the prose may still mention the word to say "no wrapper").
    token = await _mint_access_token(client)
    text = await _read_resource(client, token, "omnidim://reference/agent-config")
    assert '"requestBody": {' not in text
    assert '"transcriber": { "provider": "azure_stream" }' in text


async def test_speech_speed_range_is_documented(client: AsyncClient) -> None:
    # A speech_speed outside the provider's playable range silently mutes the
    # call (ElevenLabs: no audio outside 0.7-1.2), so the guidance must state it.
    token = await _mint_access_token(client)
    cfg = await _read_resource(client, token, "omnidim://reference/agent-config")
    assert "speech_speed" in cfg
    assert "0.7-1.2" in cfg
    routing = await _read_resource(client, token, "omnidim://guide/routing")
    assert "speech_speed" in routing
    assert "0.7-1.2" in routing


async def test_resources_never_expose_internal_infra(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 8, "method": "resources/list"},
    )
    uris = [r["uri"] for r in res.json()["result"]["resources"]]
    for uri in uris:
        text = (await _read_resource(client, token, uri)).lower()
        assert "failover" not in text, uri
        assert "gpt-5.4" not in text, uri
