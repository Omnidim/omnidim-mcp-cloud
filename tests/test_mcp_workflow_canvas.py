"""Workflow canvas: the MCP Apps view linked from the workflow tools."""
from httpx import AsyncClient

from app.procedures import WORKFLOW_CANVAS_URI

from .test_mcp_transport import _mint_access_token


async def _rpc(client: AsyncClient, method: str, params: dict | None = None) -> dict:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}},
    )
    return res.json()


async def test_workflow_tools_link_the_canvas(client: AsyncClient) -> None:
    tools = {t["name"]: t for t in (await _rpc(client, "tools/list"))["result"]["tools"]}
    for name in ("getWorkflow", "createWorkflow", "editWorkflow"):
        assert tools[name]["_meta"] == {"ui": {"resourceUri": WORKFLOW_CANVAS_URI}}, name


async def test_other_tools_carry_no_meta_key(client: AsyncClient) -> None:
    tools = {t["name"]: t for t in (await _rpc(client, "tools/list"))["result"]["tools"]}
    assert "_meta" not in tools["listWorkflows"]
    assert "_meta" not in tools["dispatchCall"]


async def test_canvas_resource_is_an_mcp_app(client: AsyncClient) -> None:
    listed = (await _rpc(client, "resources/list"))["result"]["resources"]
    assert {"uri": WORKFLOW_CANVAS_URI, "mimeType": "text/html;profile=mcp-app"}.items() <= next(
        r for r in listed if r["uri"] == WORKFLOW_CANVAS_URI
    ).items()

    read = await _rpc(client, "resources/read", {"uri": WORKFLOW_CANVAS_URI})
    content = read["result"]["contents"][0]
    assert content["mimeType"] == "text/html;profile=mcp-app"
    assert "ui/initialize" in content["text"]
    assert "const readWorkflow = " in content["text"]
