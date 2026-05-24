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
