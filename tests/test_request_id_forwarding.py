"""A dispatched tool call sends the MCP request's id to Odoo, so one id links both logs."""

from __future__ import annotations

import httpx
import structlog

from app.services import dispatcher
from app.services.bearer import ResolvedToken

TOKEN = ResolvedToken(
    odoo_user_id=7, odoo_api_key_id=1, odoo_api_key_value="key", client_id="app-1", scope=""
)


async def _sent_headers(bound_id: str | None) -> httpx.Headers:
    seen: list[httpx.Headers] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req.headers)
        return httpx.Response(200, json={"agents": []})

    transport = httpx.MockTransport(handler)
    dispatcher.set_client_factory(lambda: httpx.AsyncClient(transport=transport))
    structlog.contextvars.clear_contextvars()
    if bound_id:
        structlog.contextvars.bind_contextvars(request_id=bound_id)
    try:
        await dispatcher.dispatch_tool(name="listAgents", arguments={}, token=TOKEN)
    finally:
        structlog.contextvars.clear_contextvars()
        dispatcher.reset_client_factory()
    return seen[0]


async def test_outgoing_request_carries_the_mcp_request_id() -> None:
    assert (await _sent_headers("abc123"))["x-request-id"] == "abc123"


async def test_no_request_id_sends_no_header() -> None:
    assert "x-request-id" not in await _sent_headers(None)
