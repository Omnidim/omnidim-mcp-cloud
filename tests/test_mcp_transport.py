"""MCP transport tests: bearer gate, initialize, tools/list, tools/call.

tools/call exercises the dispatcher against a mocked backend.omnidim.io
so no real upstream traffic is generated.
"""
import base64
import hashlib
import json
import secrets
from collections.abc import Callable

import httpx
import pytest
from httpx import AsyncClient

from app._generated.tools import TOOLS
from app.services import dispatcher


@pytest.fixture
def mock_backend() -> Callable[[Callable[[httpx.Request], httpx.Response]], list[httpx.Request]]:
    """Install an httpx MockTransport into the dispatcher and capture requests.

    Returns a setup function: pass it a handler and it returns the list
    that captured requests will accumulate in. Auto-resets after the test.
    """
    captured: list[httpx.Request] = []

    def setup(handler: Callable[[httpx.Request], httpx.Response]) -> list[httpx.Request]:
        def wrapped(req: httpx.Request) -> httpx.Response:
            captured.append(req)
            return handler(req)

        transport = httpx.MockTransport(wrapped)
        dispatcher.set_client_factory(lambda: httpx.AsyncClient(transport=transport))
        return captured

    yield setup
    dispatcher.reset_client_factory()


def _make_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)[:96]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


async def _mint_access_token(client: AsyncClient) -> str:
    """Run the full register → authorize → issue-code → token dance and
    return the plaintext access_token."""
    res = await client.post(
        "/register",
        json={"redirect_uris": ["https://example.com/cb"], "client_name": "MCPTest"},
    )
    client_id = res.json()["client_id"]

    verifier, challenge = _make_pkce()
    res = await client.get(
        "/authorize",
        params={
            "client_id": client_id,
            "redirect_uri": "https://example.com/cb",
            "response_type": "code",
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "scope": "omnidim:all",
            "state": "t",
        },
        follow_redirects=False,
    )
    request_id = res.headers["location"].rsplit("=", 1)[1]

    res = await client.post(
        "/internal/issue-code",
        headers={"X-Internal-Secret": "test-shared-secret"},
        json={
            "request_id": request_id,
            "odoo_user_id": 1,
            "odoo_api_key_id": 1,
            "odoo_api_key_value": "fake-upstream-key",
            "approved_scope": "omnidim:all",
        },
    )
    code = res.json()["code"]

    res = await client.post(
        "/token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "code": code,
            "redirect_uri": "https://example.com/cb",
            "code_verifier": verifier,
        },
    )
    return res.json()["access_token"]


async def test_mcp_requires_bearer(client: AsyncClient) -> None:
    res = await client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert res.status_code == 401
    assert "WWW-Authenticate" in res.headers
    assert res.headers["WWW-Authenticate"].lower().startswith("bearer")


async def test_mcp_rejects_unknown_token(client: AsyncClient) -> None:
    res = await client.post(
        "/mcp",
        headers={"Authorization": "Bearer not-a-real-token"},
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
    )
    assert res.status_code == 401
    body = res.json()
    assert body["error"] == "invalid_token"


async def test_mcp_initialize_handshake(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == 1
    result = body["result"]
    assert result["protocolVersion"] == "2025-11-25"
    assert result["serverInfo"]["name"] == "OmniDimension"
    assert "tools" in result["capabilities"]


async def test_mcp_initialized_notification_returns_202(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
    )
    assert res.status_code == 202


async def test_mcp_tools_list_matches_generated_registry(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    )
    assert res.status_code == 200
    tools = res.json()["result"]["tools"]
    assert len(tools) == len(TOOLS)
    names_in = {t["name"] for t in tools}
    names_expected = {t["name"] for t in TOOLS}
    assert names_in == names_expected
    # Spot-check the shape of one tool.
    sample = next(t for t in tools if t["name"] == "listAgents")
    assert "inputSchema" in sample
    assert sample["inputSchema"]["type"] == "object"


async def test_mcp_tools_call_proxies_to_backend(client: AsyncClient, mock_backend) -> None:
    token = await _mint_access_token(client)
    captured = mock_backend(
        lambda req: httpx.Response(
            200,
            json={"bots": [{"id": 1, "name": "Test Agent"}], "total_records": 1},
        )
    )
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "listAgents", "arguments": {"pageno": 1}},
        },
    )
    assert len(captured) == 1
    sent = captured[0]
    assert sent.url.path == "/api/v1/agents"
    assert sent.headers["authorization"] == "Bearer fake-upstream-key"
    assert sent.url.params["pageno"] == "1"

    body = res.json()
    assert body["result"]["isError"] is False
    assert "Test Agent" in body["result"]["content"][0]["text"]


def test_path_item_params_and_ref_body_resolved() -> None:
    """Regression: path-item-level params (agent_id) and $ref request
    bodies were both dropped by the generator, so updateAgent hit a
    literal /agents/{agent_id} and documented no fields.
    """
    by_name = {t["name"]: t for t in TOOLS}
    for name in ("getAgent", "updateAgent", "deleteAgent"):
        assert by_name[name]["path_params"] == ["agent_id"], name
    update = by_name["updateAgent"]
    props = update["input_schema"]["properties"]
    assert "agent_id" in props
    assert "voice" in props
    assert set(props["voice"]["properties"]) >= {"provider", "voice_id"}


def test_all_of_request_body_flattened() -> None:
    """Regression: createAgent's body is `allOf: [$ref, {required}]`.
    The generator read `properties` off the allOf wrapper and published
    an empty input schema, leaving clients without type information for
    the nested fields.
    """
    by_name = {t["name"]: t for t in TOOLS}
    create = by_name["createAgent"]
    schema = create["input_schema"]
    assert set(schema["required"]) == {"name", "welcome_message", "context_breakdown"}
    cb = schema["properties"]["context_breakdown"]
    assert cb["type"] == "array"
    assert set(cb["items"]["required"]) == {"title", "body"}
    # No body-bearing tool may publish an empty schema.
    for tool in TOOLS:
        if tool["method"] in ("POST", "PUT"):
            assert tool["input_schema"]["properties"], tool["name"]


async def test_mcp_tools_call_substitutes_path_param(
    client: AsyncClient, mock_backend
) -> None:
    """updateAgent must PUT to /agents/<id> with agent_id removed from the
    body and the nested voice object forwarded."""
    agent_id = 158910
    token = await _mint_access_token(client)
    captured = mock_backend(
        lambda req: httpx.Response(200, json={"id": agent_id, "voice_provider": "cartesia"})
    )
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "updateAgent",
                "arguments": {
                    "agent_id": agent_id,
                    "voice": {"provider": "cartesia", "voice_id": "abc-123"},
                },
            },
        },
    )
    assert len(captured) == 1
    sent = captured[0]
    assert sent.method == "PUT"
    assert sent.url.path == f"/api/v1/agents/{agent_id}"
    sent_body = json.loads(sent.content)
    assert "agent_id" not in sent_body
    assert sent_body["voice"] == {"provider": "cartesia", "voice_id": "abc-123"}
    assert res.json()["result"]["isError"] is False


async def test_mcp_tools_call_unknown_tool(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "noSuchTool", "arguments": {}},
        },
    )
    body = res.json()
    assert body["error"]["code"] == -32602
    assert "unknown tool" in body["error"]["message"]


async def test_mcp_tools_call_redacts_api_key_in_response(
    client: AsyncClient, mock_backend
) -> None:
    token = await _mint_access_token(client)
    mock_backend(
        lambda req: httpx.Response(
            200,
            json={
                "organizations": [
                    {"id": 1, "name": "Acme", "api_key": "sk_super_secret"},
                ]
            },
        )
    )
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "listChildOrganizations", "arguments": {}},
        },
    )
    text = res.json()["result"]["content"][0]["text"]
    assert "sk_super_secret" not in text
    assert "[redacted]" in text


async def test_mcp_tools_call_redacts_credentials_in_response(
    client: AsyncClient, mock_backend
) -> None:
    """Regression: redaction must cover credential-bearing keys beyond
    the exact key `api_key`, without touching numeric counters or
    boolean placeholders.
    """
    token = await _mint_access_token(client)
    mock_backend(
        lambda req: httpx.Response(
            200,
            json={
                "bots": [
                    {
                        "id": 1,
                        "secret_key": "widget-secret-hex",
                        "total_tokens": 4044,
                        "prompt_tokens": 4005,
                        "widget_config": {
                            "iframeUrl": "https://x.io/chat-widget?secret=widget-secret-hex"
                        },
                        "integrations": [
                            {
                                "google_calendar_access_token": "ya29.live-token",
                                "google_calendar_refresh_token": "1//refresh-token",
                            }
                        ],
                        "sip_password": "sip-pass-1234",
                        "wa_access_token": "EAAG-wa-token",
                        "exotel_api_key": False,
                    }
                ]
            },
        )
    )
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "listAgents", "arguments": {}},
        },
    )
    text = res.json()["result"]["content"][0]["text"]
    for leaked in (
        "ya29.live-token",
        "1//refresh-token",
        "sip-pass-1234",
        "EAAG-wa-token",
        "widget-secret-hex",
    ):
        assert leaked not in text, leaked
    # Numeric token counters and boolean placeholders stay intact.
    assert '"total_tokens": 4044' in text
    assert '"prompt_tokens": 4005' in text
    assert '"exotel_api_key": false' in text


async def test_mcp_tools_call_coerces_stringified_structured_args(
    client: AsyncClient, mock_backend
) -> None:
    """A JSON-encoded string for an object/array-typed argument is decoded
    before forwarding, instead of being passed upstream as a string.
    """
    token = await _mint_access_token(client)
    captured = mock_backend(lambda req: httpx.Response(200, json={"id": 1}))
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "createAgent",
                "arguments": {
                    "name": "Test",
                    "welcome_message": "Hi",
                    "context_breakdown": '[{"title": "Purpose", "body": "Test."}]',
                    "voice": '{"provider": "cartesia", "voice_id": "abc"}',
                },
            },
        },
    )
    assert res.json()["result"]["isError"] is False
    sent = json.loads(captured[0].content)
    assert sent["context_breakdown"] == [{"title": "Purpose", "body": "Test."}]
    assert sent["voice"] == {"provider": "cartesia", "voice_id": "abc"}


async def test_mcp_tools_call_upstream_5xx_returns_calm_envelope(
    client: AsyncClient, mock_backend
) -> None:
    token = await _mint_access_token(client)
    mock_backend(
        lambda req: httpx.Response(
            500,
            json={
                "error": "server_error",
                "error_description": "'str' object has no attribute 'get'",
            },
        )
    )
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "listAgents", "arguments": {}},
        },
    )
    body = res.json()
    assert body["result"]["isError"] is True
    text = body["result"]["content"][0]["text"]
    assert "'str' object has no attribute 'get'" not in text
    assert '"status": 500' in text
    assert "hint" in text


async def test_mcp_tools_call_upstream_4xx_returns_is_error(
    client: AsyncClient, mock_backend
) -> None:
    token = await _mint_access_token(client)
    mock_backend(
        lambda req: httpx.Response(403, json={"error": "forbidden"})
    )
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "listAgents", "arguments": {}},
        },
    )
    body = res.json()
    assert body["result"]["isError"] is True
    assert "forbidden" in body["result"]["content"][0]["text"]
