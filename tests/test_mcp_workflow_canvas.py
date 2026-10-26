"""Workflow canvas: the MCP Apps view and the showWorkflow tool that opens it."""
import httpx
from httpx import AsyncClient

from app.procedures import WORKFLOW_CANVAS_URI

from .test_mcp_transport import _mint_access_token, mock_backend  # noqa: F401


async def _rpc(client: AsyncClient, method: str, params: dict | None = None) -> dict:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}},
    )
    return res.json()


async def _tools(client: AsyncClient) -> dict[str, dict]:
    return {t["name"]: t for t in (await _rpc(client, "tools/list"))["result"]["tools"]}


async def test_only_show_workflow_opens_the_canvas(client: AsyncClient) -> None:
    tools = await _tools(client)
    assert tools["showWorkflow"]["_meta"] == {"ui": {"resourceUri": WORKFLOW_CANVAS_URI}}
    for name in ("getWorkflow", "createWorkflow", "editWorkflow", "listWorkflows", "dispatchCall"):
        assert "_meta" not in tools[name], name


async def test_show_workflow_takes_only_a_workflow_id(client: AsyncClient) -> None:
    show = (await _tools(client))["showWorkflow"]
    assert show["inputSchema"]["required"] == ["workflow_id"]
    assert list(show["inputSchema"]["properties"]) == ["workflow_id"]
    assert show["annotations"]["readOnlyHint"] is True
    assert show["annotations"]["title"] == "Show workflow canvas"


async def test_show_workflow_reads_the_workflow(client: AsyncClient, mock_backend) -> None:  # noqa: F811
    token = await _mint_access_token(client)
    captured = mock_backend(lambda req: httpx.Response(200, json={"workflow": {"id": 7}}))
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "showWorkflow", "arguments": {"workflow_id": 7}},
        },
    )
    assert res.json()["result"]["isError"] is False
    assert captured[0].method == "GET"
    assert captured[0].url.raw_path == b"/api/v1/workflows/7"


async def test_canvas_resource_is_an_mcp_app(client: AsyncClient) -> None:
    listed = (await _rpc(client, "resources/list"))["result"]["resources"]
    entry = next(r for r in listed if r["uri"] == WORKFLOW_CANVAS_URI)
    assert entry["mimeType"] == "text/html;profile=mcp-app"

    read = await _rpc(client, "resources/read", {"uri": WORKFLOW_CANVAS_URI})
    content = read["result"]["contents"][0]
    assert content["mimeType"] == "text/html;profile=mcp-app"
    assert "ui/initialize" in content["text"]
    assert "const editArgs = " in content["text"]
    assert "if (event.source !== window.parent) return;" in content["text"]
