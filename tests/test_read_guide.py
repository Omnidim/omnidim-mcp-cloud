from typing import Any

from httpx import AsyncClient

from app.procedures import build_prompt, read_resource
from app.routes.mcp import INSTRUCTIONS

from .test_mcp_transport import _mint_access_token


async def _rpc(client: AsyncClient, method: str, params: Any = None, path: str = "/mcp") -> Any:
    token = await _mint_access_token(client)
    res = await client.post(
        path,
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}},
    )
    return res.json()


async def _read_guide(client: AsyncClient, arguments: dict[str, Any]) -> Any:
    return await _rpc(client, "tools/call", {"name": "readGuide", "arguments": arguments})


async def test_read_guide_is_listed_read_only_on_both_endpoints(client: AsyncClient) -> None:
    for path in ("/mcp", "/mcp/readonly"):
        listed = (await _rpc(client, "tools/list", path=path))["result"]["tools"]
        tools = {t["name"]: t for t in listed}
        assert tools["readGuide"]["annotations"]["readOnlyHint"] is True


async def test_read_guide_names_every_playbook_and_guide(client: AsyncClient) -> None:
    tools = {t["name"]: t for t in (await _rpc(client, "tools/list"))["result"]["tools"]}
    names = tools["readGuide"]["inputSchema"]["properties"]["name"]["enum"]
    prompts = [p["name"] for p in (await _rpc(client, "prompts/list"))["result"]["prompts"]]
    guides = [
        r["uri"]
        for r in (await _rpc(client, "resources/list"))["result"]["resources"]
        if r["mimeType"] == "text/markdown"
    ]
    assert sorted(names) == sorted(prompts + guides)


async def test_read_guide_returns_the_playbook_steps(client: AsyncClient) -> None:
    body = await _read_guide(client, {"name": "provision_agent"})
    text = body["result"]["content"][0]["text"]
    prompt = build_prompt("provision_agent", {})
    assert prompt is not None
    assert prompt["messages"][0]["content"]["text"] in text
    assert "omnidim://guide/call-tips" in text


async def test_read_guide_returns_a_guide_by_its_link(client: AsyncClient) -> None:
    body = await _read_guide(client, {"name": "omnidim://guide/call-tips"})
    text = body["result"]["content"][0]["text"]
    resource = read_resource("omnidim://guide/call-tips")
    assert resource is not None
    assert text == resource["contents"][0]["text"]


async def test_read_guide_refuses_an_unknown_name(client: AsyncClient) -> None:
    body = await _read_guide(client, {"name": "omnidim://guide/nope"})
    assert body["error"]["code"] == -32602
    assert "provision_agent" in body["error"]["message"]


async def test_read_guide_refuses_a_missing_name(client: AsyncClient) -> None:
    body = await _read_guide(client, {})
    assert body["error"]["code"] == -32602


async def test_read_guide_needs_a_bearer(client: AsyncClient) -> None:
    res = await client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "readGuide", "arguments": {"name": "provision_agent"}},
        },
    )
    assert res.status_code == 401


def test_instructions_send_every_session_to_the_playbooks() -> None:
    assert "readGuide" in INSTRUCTIONS
    for playbook in ("provision_agent", "build_outbound_campaign", "build_workflow", "audit_calls"):
        assert playbook in INSTRUCTIONS
