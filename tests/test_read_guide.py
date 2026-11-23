from typing import Any

import pytest
from httpx import AsyncClient

from app.procedures import GUIDE_NAMES, build_prompt, guide_text, read_resource
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


async def _read_guide(
    client: AsyncClient, arguments: dict[str, Any], path: str = "/mcp"
) -> Any:
    params = {"name": "readGuide", "arguments": arguments}
    return await _rpc(client, "tools/call", params, path=path)


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
    assert "placeholder" in text
    assert "with `readGuide`" in text


@pytest.mark.parametrize("name", GUIDE_NAMES)
def test_every_name_reads_back_text(name: str) -> None:
    assert guide_text(name)


async def test_read_guide_runs_on_the_read_only_endpoint(client: AsyncClient) -> None:
    body = await _read_guide(client, {"name": "audit_calls"}, path="/mcp/readonly")
    assert "listCallLogs" in body["result"]["content"][0]["text"]


async def test_read_guide_returns_a_guide_by_its_link(client: AsyncClient) -> None:
    body = await _read_guide(client, {"name": "omnidim://guide/call-tips"})
    text = body["result"]["content"][0]["text"]
    resource = read_resource("omnidim://guide/call-tips")
    assert resource is not None
    assert text.endswith(resource["contents"][0]["text"])
    assert "with `readGuide`" in text


async def test_read_guide_refuses_an_unknown_name(client: AsyncClient) -> None:
    body = await _read_guide(client, {"name": "omnidim://guide/nope"})
    assert body["error"]["code"] == -32602
    assert "provision_agent" in body["error"]["message"]


@pytest.mark.parametrize("arguments", [{}, {"name": 5}, {"name": ["provision_agent"]}])
async def test_read_guide_refuses_a_name_that_is_not_text(
    client: AsyncClient, arguments: dict[str, Any]
) -> None:
    body = await _read_guide(client, arguments)
    assert body["error"]["code"] == -32602


def test_instructions_send_every_session_to_the_playbooks() -> None:
    assert "readGuide" in INSTRUCTIONS
    for name in (
        "provision_agent",
        "build_outbound_campaign",
        "build_workflow",
        "audit_calls",
        "restore_agent_version",
        "omnidim://guide/routing",
    ):
        assert name in INSTRUCTIONS
        assert name in GUIDE_NAMES
