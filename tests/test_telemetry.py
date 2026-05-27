from httpx import AsyncClient


async def test_telemetry_accepts_install(client: AsyncClient) -> None:
    res = await client.post(
        "/api/telemetry/event",
        json={
            "event": "install",
            "install_id": "abc12345xyz",
            "package": "@omnidim-ai/mcp-server",
            "package_version": "0.2.5",
            "node_version": "20.18.0",
            "os_platform": "darwin",
            "os_arch": "arm64",
        },
    )
    assert res.status_code == 204


async def test_telemetry_accepts_session_end_with_tools(client: AsyncClient) -> None:
    res = await client.post(
        "/api/telemetry/event",
        json={
            "event": "session_end",
            "install_id": "abc12345xyz",
            "package": "@omnidim-ai/mcp-server",
            "package_version": "0.2.5",
            "duration_s": 245,
            "tools_called": [
                {"tool": "listAgents", "count": 12},
                {"tool": "dispatchCall", "count": 3},
            ],
        },
    )
    assert res.status_code == 204


async def test_telemetry_accepts_setup_client_failure(client: AsyncClient) -> None:
    res = await client.post(
        "/api/telemetry/event",
        json={
            "event": "setup_client_result",
            "install_id": "abc12345xyz",
            "package": "@omnidim-ai/mcp-server",
            "package_version": "0.3.0",
            "client": "claude_desktop",
            "outcome": "failed",
            "error_code": "config_write_error",
            "error_class": "Error",
        },
    )
    assert res.status_code == 204


async def test_telemetry_accepts_session_crash_with_tool_errors(client: AsyncClient) -> None:
    res = await client.post(
        "/api/telemetry/event",
        json={
            "event": "session_crash",
            "install_id": "abc12345xyz",
            "package": "@omnidim-ai/mcp-server",
            "package_version": "0.3.0",
            "phase": "runtime",
            "error_class": "TypeError",
            "error_code": "unknown",
            "duration_s": 12,
            "tool_errors_total": 2,
            "tools_called": [
                {
                    "tool": "listAgents",
                    "count": 3,
                    "ok": 2,
                    "errors": [{"code": "http_500", "count": 1}],
                },
            ],
        },
    )
    assert res.status_code == 204


async def test_telemetry_rejects_unknown_event(client: AsyncClient) -> None:
    res = await client.post(
        "/api/telemetry/event",
        json={
            "event": "wat",
            "install_id": "abc12345xyz",
            "package": "@omnidim-ai/mcp-server",
            "package_version": "0.2.5",
        },
    )
    assert res.status_code == 422


async def test_telemetry_rejects_short_install_id(client: AsyncClient) -> None:
    res = await client.post(
        "/api/telemetry/event",
        json={
            "event": "install",
            "install_id": "short",
            "package": "@omnidim-ai/mcp-server",
            "package_version": "0.2.5",
        },
    )
    assert res.status_code == 422
