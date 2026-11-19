"""The MCP log names the AI app behind every request and records every error we return.

Grafana's MCP board groups tool calls by app (Claude, ChatGPT, Cursor, ...) and lists the
errors AI apps hit before a tool runs: bad arguments, unknown tools, failed sign-in checks.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from httpx import AsyncClient

from app.routes import mcp as mcp_route
from app.services import dispatcher
from tests.test_mcp_transport import _mint_access_token, mock_backend  # noqa: F401


class _Recorder:
    """Stands in for a module's structlog logger and keeps every call."""

    def __init__(self) -> None:
        self.lines: list[dict[str, Any]] = []

    def _record(self, event: str, **fields: Any) -> None:
        self.lines.append({"event": event, **fields})

    info = warning = error = _record

    def named(self, event: str) -> list[dict[str, Any]]:
        return [line for line in self.lines if line["event"] == event]


@pytest.fixture
def logs(monkeypatch: pytest.MonkeyPatch) -> _Recorder:
    recorder = _Recorder()
    monkeypatch.setattr(mcp_route, "log", recorder)
    monkeypatch.setattr(dispatcher, "log", recorder)
    return recorder


async def _call(client: AsyncClient, token: str, method: str, params: Any) -> httpx.Response:
    return await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
    )


async def test_tool_lines_name_the_app(client: AsyncClient, mock_backend, logs) -> None:  # noqa: F811
    token = await _mint_access_token(client)
    mock_backend(lambda req: httpx.Response(200, json={"agents": []}))

    await _call(client, token, "tools/call", {"name": "listAgents", "arguments": {}})

    for event in ("mcp_request", "tool_call", "tool_result"):
        assert [line["client_name"] for line in logs.named(event)] == ["MCPTest"], event


async def test_unknown_tool_logs_one_error(client: AsyncClient, logs) -> None:
    token = await _mint_access_token(client)

    res = await _call(client, token, "tools/call", {"name": "noSuchTool", "arguments": {}})

    assert res.json()["error"]["code"] == -32602
    errors = logs.named("mcp_error")
    assert len(errors) == 1
    assert errors[0]["method"] == "tools/call"
    assert errors[0]["tool"] == "noSuchTool"
    assert errors[0]["code"] == -32602
    assert "unknown tool" in errors[0]["message"]
    assert errors[0]["client_name"] == "MCPTest"


async def test_bad_arguments_and_unknown_method_log_errors(client: AsyncClient, logs) -> None:
    token = await _mint_access_token(client)

    await _call(client, token, "tools/call", {"name": "listAgents", "arguments": "oops"})
    await _call(client, token, "no/such/method", {})

    assert [(e["method"], e["code"]) for e in logs.named("mcp_error")] == [
        ("tools/call", -32602),
        ("no/such/method", -32601),
    ]


async def test_success_logs_no_error(client: AsyncClient, mock_backend, logs) -> None:  # noqa: F811
    token = await _mint_access_token(client)
    mock_backend(lambda req: httpx.Response(200, json={"agents": []}))

    await _call(client, token, "tools/call", {"name": "listAgents", "arguments": {}})
    await _call(client, token, "tools/list", {})

    assert logs.named("mcp_error") == []


async def test_failed_sign_in_check_logs_the_reason(client: AsyncClient, logs) -> None:
    res = await _call(client, "not-a-real-token", "tools/list", {})

    assert res.status_code == 401
    assert [line["reason"] for line in logs.named("mcp_auth_failed")] == [
        "access token not recognised"
    ]
